/**
 * API URL Configuration
 * 
 * Detecta automáticamente la URL del backend basándose en:
 * 1. Variable de entorno VITE_API_URL (si está definida)
 * 2. El hostname desde donde se accede al frontend (puerto 8000)
 * 
 * Esto permite que la aplicación funcione en cualquier entorno sin configuración manual:
 * - Desarrollo local: http://localhost:8000
 * - Raspberry Pi: http://192.168.1.X:8000
 * - Producción: http://dominio.com:8000
 */

export const getApiUrl = (): string => {
    // Si hay variable de entorno definida, úsala
    if (import.meta.env.VITE_API_URL) {
        return import.meta.env.VITE_API_URL;
    }

    // Si estamos en el navegador, usa el mismo host desde donde se accede
    if (typeof window !== 'undefined') {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}:8000`;
    }

    // Fallback para SSR (aunque Vite no hace SSR por defecto)
    return 'http://localhost:8000';
};

export const API_URL = getApiUrl();
