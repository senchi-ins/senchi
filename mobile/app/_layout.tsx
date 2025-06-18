import { Stack } from "expo-router";
import { Colours } from "../constants/colors";

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: Colours.light.background,
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="index" 
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="quote/index" 
        options={{ 
          headerShown: false,
          // presentation: 'modal',
          animation: 'slide_from_bottom',
          animationDuration: 350,
          gestureEnabled: false
        }}
      />
    </Stack>
  )
}
