import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import {FRONTEND_BUILD_LABEL} from './buildInfo';
import './index.css';

if (import.meta.env.PROD) {
  console.info('[ClinicMonitoring] frontend build:', FRONTEND_BUILD_LABEL);
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
