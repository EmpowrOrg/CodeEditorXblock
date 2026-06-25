// Bundles src/index.tsx (+ vendored AssessmentPlayer + React) into one IIFE the XBlock serves.
// Output: ../assessmentplugin/static/js/dist/bundle.js
import {build, context} from "esbuild";
import {fileURLToPath} from "node:url";
import {dirname, resolve} from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const outfile = resolve(here, "../assessmentplugin/static/js/dist/bundle.js");

/** @type {import('esbuild').BuildOptions} */
const options = {
    entryPoints: [resolve(here, "src/index.tsx")],
    outfile,
    bundle: true,
    format: "iife",          // self-executing: defines window.AssessmentXBlock, no module loader needed
    target: ["es2019"],
    jsx: "automatic",        // matches tsconfig "react-jsx"
    minify: true,
    sourcemap: false,
    logLevel: "info",
    define: {"process.env.NODE_ENV": '"production"'},
};

const watch = process.argv.includes("--watch");

if (watch) {
    const ctx = await context(options);
    await ctx.watch();
    console.log("watching… rebuilding bundle.js on change");
} else {
    await build(options);
    console.log("built", outfile);
}
