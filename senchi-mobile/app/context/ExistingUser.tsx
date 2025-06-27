import { createContext, useContext } from 'react';

export const ExistingUserContext = createContext({
  isExistingUser: false,
  setIsExistingUser: (existingUser: boolean) => {},
});

export const useExistingUser = () => useContext(ExistingUserContext); 