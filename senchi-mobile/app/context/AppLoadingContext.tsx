import { createContext, useContext } from 'react';

export const AppLoadingContext = createContext({
  appIsReady: false,
  setAppIsReady: (ready: boolean) => {},
});

export const useAppLoading = () => useContext(AppLoadingContext); 