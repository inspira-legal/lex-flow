import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// Check if we're building the library
const isLibraryBuild = process.env.BUILD_LIB === 'true'
const isUmdBuild = process.env.BUILD_UMD === 'true'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: isLibraryBuild ? '/' : '/static/',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  define: {
    // Replace version placeholder at build time
    '__VERSION__': JSON.stringify(process.env.npm_package_version || '0.0.0'),
    // Replace process.env for browser compatibility
    'process.env.NODE_ENV': JSON.stringify('production'),
    'process.env': JSON.stringify({}),
  },
  build: isLibraryBuild
    ? {
        // Library build configuration
        lib: {
          entry: path.resolve(__dirname, 'src/lib/index.ts'),
          name: 'LexFlowEditor',
          formats: isUmdBuild ? ['umd'] : ['es'],
          fileName: (format) => `lexflow-editor.${format}.js`,
        },
        rollupOptions: {
          // Externalize React for ES build (bundled for UMD)
          external: isUmdBuild
            ? []
            : ['react', 'react-dom', 'react/jsx-runtime'],
          output: {
            // Global variables for UMD build
            globals: isUmdBuild
              ? {}
              : {
                  react: 'React',
                  'react-dom': 'ReactDOM',
                  'react/jsx-runtime': 'jsxRuntime',
                },
            // Prevent code splitting - create single bundle
            inlineDynamicImports: isUmdBuild,
            // Ensure CSS is extracted
            assetFileNames: (assetInfo) => {
              if (assetInfo.name?.endsWith('.css')) {
                return 'lexflow-editor.css'
              }
              return assetInfo.name ?? 'assets/[name].[ext]'
            },
          },
        },
        // Output to dist for library
        outDir: 'dist',
        emptyOutDir: !isUmdBuild, // Only clear on first build
        // Generate sourcemaps for debugging
        sourcemap: true,
        // Minify for production
        minify: 'esbuild',
      }
    : {
        // Default SPA build configuration
        outDir: '../src/lexflow_web/static',
        emptyOutDir: true,
      },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
