"""Apollo.io API opcodes for LexFlow.

This module provides opcodes for interacting with the Apollo.io API,
enabling lead generation and enrichment workflows.

Authentication:
    Apollo uses API key authentication via the X-Api-Key header.
    Get your key at: https://developer.apollo.io
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from .opcodes import opcode, register_category

logger = logging.getLogger(__name__)

try:
    import aiohttp

    APOLLO_AVAILABLE = True
except ImportError:
    APOLLO_AVAILABLE = False


APOLLO_API_BASE_URL = "https://api.apollo.io"

# =============================================================================
# Legal industry defaults (used by apollo_search_law_firms / legal_people)
# =============================================================================

BRAZILIAN_STATES = [
    "acre", "alagoas", "amapá", "amazonas", "bahia", "ceará",
    "distrito federal", "espírito santo", "goiás", "maranhão",
    "mato grosso", "mato grosso do sul", "minas gerais", "pará",
    "paraíba", "paraná", "pernambuco", "piauí", "rio de janeiro",
    "rio grande do norte", "rio grande do sul", "rondônia", "roraima",
    "santa catarina", "são paulo", "sergipe", "tocantins",
]

DEFAULT_LEGAL_INDUSTRIES = ["law practice", "legal services"]

DEFAULT_LEGAL_SIC_CODES = ["8111"]

# Apollo accepts up to 150 keyword tags per request.
DEFAULT_LEGAL_KEYWORDS = [
    # Português: áreas de atuação e serviços jurídicos
    "advocacia empresarial", "assessoria jurídica", "consultoria jurídica",
    "consultoria empresarial", "direito civil", "direito penal",
    "direito tributário", "direito trabalhista",
    "direito trabalhista empresarial", "direito administrativo",
    "direito previdenciario", "direito societário",
    "direito penal economico", "direito do consumidor",
    "direito imobiliário", "contencioso estrategico", "contencioso civel",
    "recuperacao judicial", "restruturacao e insolvencia",
    "societario e ma", "concorrencial", "contratos comerciais",
    "contratos empresariais", "compliance empresarial",
    "consultoria em compliance e governança corporativa",
    "reorganizacao societaria", "fusão e aquisição de empresas",
    "responsabilidade civil", "propriedade intelectual",
    "planejamento tributario", "planejamento sucessório", "due diligence",
    "due diligence em operações societárias",
    "gestão de riscos jurídicos", "proteção empresarial",
    "defesa judicial", "ações judiciais", "ações de despejo",
    "ações de responsabilidade civil empresarial",
    "fiscal e tributário", "recuperação de créditos fiscais",
    "recuperação de créditos tributários", "negociação de créditos",
    "negociação de créditos homologados", "análise de créditos de icms",
    "defesas administrativas e judiciais tributárias",
    "direitos creditorios", "regularização imobiliária",
    "regularização de imóveis e loteamentos",
    "análise e elaboração de contratos de franquia",
    "registro de marcas e patentes", "registro de direitos autorais",
    "arbitragem comercial",
    # Inglês: termos core de escritórios de advocacia
    "law firm", "law practice", "legal services", "offices of lawyers",
    "corporate law", "business law", "litigation", "litigation strategy",
    "strategic litigation", "high-stakes litigation",
    "complex corporate litigation", "litigation support",
    "judicial litigation", "tax litigation", "mergers and acquisitions",
    "m&a", "corporate governance", "regulatory compliance",
    "legal compliance", "corporate legal compliance", "legal counsel",
    "legal advisory", "legal advisory services", "legal consulting",
    "legal consulting services", "legal consultancy",
    "legal representation", "legal defense", "legal advocacy",
    "legal strategy", "strategic legal planning", "legal planning",
    "corporate legal strategy", "legal technology",
    "law firm technology", "law firm management",
    "legal risk management", "corporate legal risk mitigation",
    "corporate legal advice", "corporate criminal defense",
    "corporate criminal law", "criminal business law",
    "legal case strategy", "legal case management", "legal analysis",
    "legal research", "legal expertise", "legal innovation",
    "legal advice", "legal documentation", "legal document review",
    "legal process automation", "legal project management",
    "legal negotiations", "lawyer expertise", "lawyer team",
    # Inglês: áreas especializadas
    "labor law", "tax law", "tax planning", "tax dispute resolution",
    "tax transaction advisory", "administrative law",
    "administrative appeals", "environmental law",
    "environmental law for companies", "financial law",
    "financial compliance", "public law", "public law compliance",
    "public procurement law", "public bidding",
    "public tender interpretation", "insolvency law",
    "restructuring and insolvency", "company restructuring",
    "debt restructuring", "company debt renegotiation",
    "contract drafting", "contract negotiation", "commercial contracts",
    "commercial leases", "franchising", "intellectual property",
    "consumer protection", "arbitration", "dispute resolution",
    "conflict resolution", "dispute management",
    "legal dispute handling", "legal dispute resolution",
    "complex legal disputes", "court representation", "trial advocacy",
    "judicial recovery", "judicial process",
    "judicial and administrative litigation", "corporate transactions",
]

DEFAULT_LEGAL_TITLES = [
    # Português — Sócios e Fundadores (Decisores)
    "Sócio", "Socia", "Sócio Fundador", "Sócia Fundadora",
    "Sócio Diretor", "Sócia Diretora", "Sócio Administrador",
    "Sócia Administradora", "Advogado Sócio", "Advogada Sócia",
    # Inglês — Sócios (Decisores)
    "Partner", "Managing Partner", "Founding Partner",
    "Senior Partner", "Equity Partner", "Name Partner",
    # Português — Advogados Seniores
    "Advogado", "Advogada", "Advogado Senior", "Advogada Senior",
    "Advogado Sênior", "Advogada Sênior", "Advogado Pleno",
    "Advogada Plena", "Advogado Associado", "Advogada Associada",
    # Inglês — Advogados
    "Lawyer", "Attorney", "Senior Lawyer", "Senior Attorney",
    "Associate", "Senior Associate", "Of Counsel",
    # Português — Liderança Jurídica (Decisores)
    "Diretor Jurídico", "Diretora Jurídica", "Coordenador Jurídico",
    "Coordenadora Jurídica", "Gerente Jurídico", "Gerente Jurídica",
    "Consultor Jurídico", "Consultora Jurídica", "Conselheiro",
    "Conselheira",
    # Inglês — Liderança Jurídica (Decisores)
    "Counsel", "Legal Counsel", "General Counsel", "Senior Counsel",
    "Chief Legal Officer", "Legal Director", "Legal Manager",
    "Legal Consultant",
]


def _build_excluded_brazilian_states(
    locations: List[str],
) -> List[str]:
    """Build list of Brazilian states to exclude based on selected locations.

    When the user selects specific Brazilian states, automatically exclude
    all other states to improve Apollo search precision.

    Args:
        locations: User-selected location strings.

    Returns:
        List of state names to exclude, or empty if no BR state was matched.
    """
    locations_lower = [loc.lower() for loc in locations]

    matched = [
        state for state in BRAZILIAN_STATES
        if any(state in loc for loc in locations_lower)
    ]

    if not matched:
        return []

    return [state for state in BRAZILIAN_STATES if state not in matched]


class ApolloClient:
    """Reusable Apollo.io API client."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = APOLLO_API_BASE_URL
        self._session = aiohttp.ClientSession(
            headers={"X-Api-Key": api_key},
        )

    def __repr__(self) -> str:
        return "ApolloClient(api_key=***)"

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Make a POST request to Apollo API.

        Args:
            endpoint: API endpoint path.
            json_data: JSON body payload.
            params: URL query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            ValueError: If the API returns an error status.
        """
        url = f"{self.base_url}{endpoint}"

        async with self._session.post(
            url, json=json_data, params=params
        ) as response:
            if response.status == 204:
                return {}

            data = await response.json()

            if response.status >= 400:
                error_msg = data.get("message", data.get("error", "Unknown error"))
                raise ValueError(
                    f"Apollo API error ({response.status}): {error_msg}"
                )

            return data


def _build_query_params(data: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Build flat query params, expanding lists with [] suffix.

    Apollo's people search endpoint expects array params as repeated keys
    with [] suffix (e.g., organization_ids[]=id1&organization_ids[]=id2).

    Args:
        data: Dictionary of parameters.

    Returns:
        List of (key, value) tuples compatible with aiohttp params.
    """
    params: List[Tuple[str, str]] = []
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, list):
            for item in value:
                params.append((f"{key}[]", str(item)))
        else:
            params.append((key, str(value)))
    return params


def register_apollo_opcodes():
    """Register Apollo opcodes to the default registry."""
    if not APOLLO_AVAILABLE:
        return

    register_category(
        id="apollo",
        label="Apollo.io",
        prefix="apollo_",
        color="#4A90D9",
        icon="🚀",
        requires="http",
        order=220,
    )

    # ============================================================================
    # Authentication
    # ============================================================================

    @opcode(category="apollo")
    async def apollo_create_client(
        api_key: str,
    ) -> ApolloClient:
        """Create an Apollo.io API client for lead generation.

        Args:
            api_key: Apollo.io API key.

        Returns:
            ApolloClient object to use with other apollo_* opcodes.

        Example:
            api_key: "xxxxxxxxxxxxxxxxxxxxxxxxxx"
        """
        if not api_key:
            raise ValueError(
                "api_key is required. "
                "Get your key at: https://developer.apollo.io"
            )

        return ApolloClient(api_key)

    @opcode(category="apollo")
    async def apollo_close_client(client: ApolloClient) -> bool:
        """Close an Apollo client and release its resources.

        Args:
            client: ApolloClient to close.

        Returns:
            True when the client session is closed.
        """
        await client._session.close()
        return True

    # ============================================================================
    # Company Search
    # ============================================================================

    @opcode(category="apollo")
    async def apollo_search_companies(
        client: ApolloClient,
        organization_locations: Optional[List[str]] = None,
        organization_not_locations: Optional[List[str]] = None,
        organization_num_employees_ranges: Optional[List[str]] = None,
        organization_industries: Optional[List[str]] = None,
        q_organization_keyword_tags: Optional[List[str]] = None,
        q_organization_sic_codes: Optional[List[str]] = None,
        currently_using_any_of_technology_uids: Optional[List[str]] = None,
        organization_ids: Optional[List[str]] = None,
        q_organization_name: Optional[List[str]] = None,
        revenue_range_min: Optional[int] = None,
        revenue_range_max: Optional[int] = None,
        total_funding_range_min: Optional[int] = None,
        total_funding_range_max: Optional[int] = None,
        per_page: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search for companies on Apollo.io.

        Args:
            client: ApolloClient from apollo_create_client.
            organization_locations: List of location strings (e.g., ["Brazil", "São Paulo, Brazil"]).
            organization_not_locations: Locations to exclude from results.
            organization_num_employees_ranges: Employee count ranges (e.g., ["1,10", "11,50"]).
            organization_industries: Industry filters (e.g., ["legal services"]).
            q_organization_keyword_tags: Keyword tags to filter by.
            q_organization_sic_codes: SIC code filters.
            currently_using_any_of_technology_uids: Technology UID filters.
            organization_ids: Specific organization IDs to search.
            q_organization_name: Organization name search terms.
            revenue_range_min: Minimum revenue filter.
            revenue_range_max: Maximum revenue filter.
            total_funding_range_min: Minimum total funding filter.
            total_funding_range_max: Maximum total funding filter.
            per_page: Results per page (default: 100).
            page: Page number (default: 1).

        Returns:
            Dict with model_ids (company IDs), organizations (company details),
            and breadcrumbs (search metadata).

        Example:
            client: { node: create_client }
            organization_locations: ["Brazil"]
            organization_industries: ["legal services"]
            per_page: 100
            page: 1
        """
        body: Dict[str, Any] = {
            "per_page": per_page,
            "page": page,
        }

        if organization_locations:
            body["organization_locations"] = organization_locations
        if organization_not_locations:
            body["organization_not_locations"] = organization_not_locations
        if organization_num_employees_ranges:
            body["organization_num_employees_ranges"] = organization_num_employees_ranges
        if organization_industries:
            body["organization_industries"] = organization_industries
        if q_organization_keyword_tags:
            body["q_organization_keyword_tags"] = q_organization_keyword_tags
        if q_organization_sic_codes:
            body["q_organization_sic_codes"] = q_organization_sic_codes
        if currently_using_any_of_technology_uids:
            body["currently_using_any_of_technology_uids"] = (
                currently_using_any_of_technology_uids
            )
        if organization_ids:
            body["organization_ids"] = organization_ids
        if q_organization_name:
            body["q_organization_name"] = q_organization_name
        if revenue_range_min is not None:
            body["revenue[min]"] = revenue_range_min
        if revenue_range_max is not None:
            body["revenue[max]"] = revenue_range_max
        if total_funding_range_min is not None:
            body["total_funding_range[min]"] = total_funding_range_min
        if total_funding_range_max is not None:
            body["total_funding_range[max]"] = total_funding_range_max

        return await client.post("/v1/organizations/search", json_data=body)

    # ============================================================================
    # People Search
    # ============================================================================

    @opcode(category="apollo")
    async def apollo_search_people(
        client: ApolloClient,
        organization_ids: Optional[List[str]] = None,
        person_titles: Optional[List[str]] = None,
        person_locations: Optional[List[str]] = None,
        contact_email_status: Optional[List[str]] = None,
        person_seniorities: Optional[List[str]] = None,
        per_page: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search for people on Apollo.io.

        Args:
            client: ApolloClient from apollo_create_client.
            organization_ids: List of Apollo organization IDs to search within.
            person_titles: Job title filters (e.g., ["Sócio", "Advogado"]).
            person_locations: Location filters for people.
            contact_email_status: Email status filters (e.g., ["verified"]).
            person_seniorities: Seniority level filters.
            per_page: Results per page (default: 100).
            page: Page number (default: 1).

        Returns:
            Dict with people list containing id, first_name, last_name, title.

        Example:
            client: { node: create_client }
            organization_ids: ["org_123", "org_456"]
            person_titles: ["Sócio", "Advogado Senior"]
            contact_email_status: ["verified"]
        """
        params_data: Dict[str, Any] = {
            "per_page": per_page,
            "page": page,
        }

        if organization_ids:
            params_data["organization_ids"] = organization_ids
        if person_titles:
            params_data["person_titles"] = person_titles
        if person_locations:
            params_data["person_locations"] = person_locations
        if contact_email_status:
            params_data["contact_email_status"] = contact_email_status
        if person_seniorities:
            params_data["person_seniorities"] = person_seniorities

        query_params = _build_query_params(params_data)

        return await client.post(
            "/v1/mixed_people/api_search",
            params=query_params,
        )

    # ============================================================================
    # People Enrichment
    # ============================================================================

    @opcode(category="apollo")
    async def apollo_enrich_people(
        client: ApolloClient,
        person_ids: List[str],
        reveal_personal_emails: bool = True,
        chunk_size: int = 10,
    ) -> List[Dict[str, Any]]:
        """Enrich people data with full contact and company details.

        Calls Apollo's bulk_match endpoint in chunks to retrieve complete
        person and organization data including emails, phones, and company info.

        Args:
            client: ApolloClient from apollo_create_client.
            person_ids: List of Apollo person IDs to enrich.
            reveal_personal_emails: Include personal emails in results (default: True).
            chunk_size: Number of IDs per API call (default: 10, max: 10).

        Returns:
            List of enriched person dicts with full contact and company details.
            Each dict contains person fields (first_name, last_name, title, email,
            email_status, linkedin_url, city, state, country, seniority, departments)
            and nested organization fields (name, primary_domain, website_url,
            industry, estimated_num_employees, phone, linkedin_url).

        Example:
            client: { node: create_client }
            person_ids: ["person_123", "person_456"]
            reveal_personal_emails: true
        """
        if not person_ids:
            return []

        chunk_size = min(chunk_size, 10)
        all_results: List[Dict[str, Any]] = []

        for i in range(0, len(person_ids), chunk_size):
            chunk = person_ids[i : i + chunk_size]
            details = [{"id": pid} for pid in chunk]

            params = {}
            if reveal_personal_emails:
                params["reveal_personal_emails"] = "true"

            try:
                response = await client.post(
                    "/v1/people/bulk_match",
                    json_data={"details": details},
                    params=params,
                )
                matches = response.get("matches", [])
                all_results.extend(
                    match for match in matches if match is not None
                )
            except ValueError as e:
                logger.warning(
                    "Apollo enrichment chunk failed (ids %d-%d of %d): %s",
                    i,
                    min(i + chunk_size, len(person_ids)),
                    len(person_ids),
                    e,
                )
                continue

        return all_results

    # ============================================================================
    # Legal Industry Convenience Opcodes
    # ============================================================================

    @opcode(category="apollo")
    async def apollo_search_law_firms(
        client: ApolloClient,
        locations: List[str],
        employee_ranges: Optional[List[str]] = None,
        keyword_tags: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        sic_codes: Optional[List[str]] = None,
        technology_uids: Optional[List[str]] = None,
        per_page: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search for law firms on Apollo.io with legal industry defaults.

        Convenience opcode that wraps apollo_search_companies with pre-configured
        defaults for the legal industry: 150 legal keyword tags, law practice/legal
        services industries, SIC code 8111, and automatic exclusion of non-selected
        Brazilian states.

        Args:
            client: ApolloClient from apollo_create_client.
            locations: List of location strings (e.g., ["são paulo, Brazil"]).
            employee_ranges: Employee count ranges (e.g., ["1,10", "11,50"]).
            keyword_tags: Override default legal keyword tags (150 legal terms).
            industries: Override default industries (law practice, legal services).
            sic_codes: Override default SIC codes (8111).
            technology_uids: Technology UID filters.
            per_page: Results per page (default: 100).
            page: Page number (default: 1).

        Returns:
            Dict with model_ids (company IDs), organizations (company details),
            and breadcrumbs (search metadata).

        Example:
            client: { node: create_client }
            locations: ["são paulo, Brazil"]
            employee_ranges: ["1,10", "11,50"]
            page: 1
        """
        not_locations = _build_excluded_brazilian_states(locations)

        return await apollo_search_companies(
            client=client,
            organization_locations=locations,
            organization_not_locations=not_locations or None,
            organization_num_employees_ranges=employee_ranges,
            organization_industries=industries or DEFAULT_LEGAL_INDUSTRIES,
            q_organization_keyword_tags=(
                keyword_tags or DEFAULT_LEGAL_KEYWORDS
            ),
            q_organization_sic_codes=sic_codes or DEFAULT_LEGAL_SIC_CODES,
            currently_using_any_of_technology_uids=technology_uids,
            per_page=per_page,
            page=page,
        )

    @opcode(category="apollo")
    async def apollo_search_legal_people(
        client: ApolloClient,
        organization_ids: List[str],
        person_locations: Optional[List[str]] = None,
        titles: Optional[List[str]] = None,
        per_page: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search for legal professionals on Apollo.io with legal title defaults.

        Convenience opcode that wraps apollo_search_people with pre-configured
        defaults for the legal industry: 64 legal job titles (PT/EN) and
        verified email status filter.

        Args:
            client: ApolloClient from apollo_create_client.
            organization_ids: List of Apollo organization IDs to search within.
            person_locations: Location filters for people.
            titles: Override default legal titles (51 legal roles PT/EN).
            per_page: Results per page (default: 100).
            page: Page number (default: 1).

        Returns:
            Dict with people list containing id, first_name, last_name, title.

        Example:
            client: { node: create_client }
            organization_ids: ["org_123", "org_456"]
            person_locations: ["são paulo, Brazil"]
        """
        return await apollo_search_people(
            client=client,
            organization_ids=organization_ids,
            person_titles=titles or DEFAULT_LEGAL_TITLES,
            person_locations=person_locations,
            contact_email_status=["verified"],
            per_page=per_page,
            page=page,
        )
