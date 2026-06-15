import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
// Ignore TypeScript warning for side-effect CSS import (handled by bundler)
// @ts-ignore
import "./styles/global.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
