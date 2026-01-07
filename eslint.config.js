import js from "@eslint/js";
import tseslint from "@typescript-eslint/eslint-plugin";
import tsparser from "@typescript-eslint/parser";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import prettierConfig from "eslint-config-prettier";

export default [
  js.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        // Core
        console: "readonly",
        document: "readonly",
        window: "readonly",
        fetch: "readonly",
        crypto: "readonly",
        // Timers
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        // URL/Fetch API
        URL: "readonly",
        URLSearchParams: "readonly",
        FormData: "readonly",
        Blob: "readonly",
        File: "readonly",
        Response: "readonly",
        Request: "readonly",
        Headers: "readonly",
        AbortController: "readonly",
        AbortSignal: "readonly",
        // Events
        Event: "readonly",
        EventTarget: "readonly",
        CustomEvent: "readonly",
        MessageEvent: "readonly",
        DOMException: "readonly",
        // Media/Audio
        MediaStream: "readonly",
        MediaRecorder: "readonly",
        WebSocket: "readonly",
        Audio: "readonly",
        AudioContext: "readonly",
        AnalyserNode: "readonly",
        ScriptProcessorNode: "readonly",
        SpeechSynthesisUtterance: "readonly",
        HTMLAudioElement: "readonly",
        // WebRTC
        RTCPeerConnection: "readonly",
        RTCDataChannel: "readonly",
        RTCIceServer: "readonly",
        RTCStatsReport: "readonly",
        // Storage/Navigation
        navigator: "readonly",
        localStorage: "readonly",
        sessionStorage: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": tseslint,
      react: reactPlugin,
      "react-hooks": reactHooksPlugin,
    },
    rules: {
      ...tseslint.configs.recommended.rules,
      ...reactPlugin.configs.recommended.rules,
      ...reactHooksPlugin.configs.recommended.rules,
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/explicit-module-boundary-types": "off",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
      "no-console": ["warn", { allow: ["warn", "error"] }],
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
  {
    ignores: [
      "node_modules/",
      "dist/",
      ".venv/",
      "__pycache__/",
      "*.config.js",
      "*.config.ts",
    ],
  },
  prettierConfig,
];
