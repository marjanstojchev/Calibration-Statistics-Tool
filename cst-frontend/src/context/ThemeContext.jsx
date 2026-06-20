import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
    const [theme, setTheme] = useState(() => localStorage.getItem('cst-theme') || 'system');

    useEffect(() => {
        const apply = (t) => {
            let resolved = t;
            if (t === 'system') {
                resolved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            }
            document.documentElement.setAttribute('data-theme', resolved);
        };

        apply(theme);
        localStorage.setItem('cst-theme', theme);

        const mq = window.matchMedia('(prefers-color-scheme: dark)');
        const handler = () => { if (theme === 'system') apply('system'); };
        mq.addEventListener('change', handler);
        return () => mq.removeEventListener('change', handler);
    }, [theme]);

    return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

export const useTheme = () => useContext(ThemeContext);
