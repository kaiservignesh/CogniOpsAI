import { createContext } from "react";

export type ThemeMode = "light" | "dark";

export interface AppThemeContextValue {
  mode: ThemeMode;
  toggleTheme: () => void;
}

export const AppThemeContext = createContext<
  AppThemeContextValue | undefined
>(undefined);
