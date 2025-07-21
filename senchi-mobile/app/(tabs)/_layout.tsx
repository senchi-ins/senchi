import { Colours } from '@/constants/colours';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { BlurView } from 'expo-blur';
import { useRouter, Tabs } from 'expo-router';
import { StyleSheet, Dimensions } from 'react-native';
import { useState, useEffect } from 'react';
import Onboarding from '../sections/onboarding/onboarding';
import SplashScreen from '@/animations/splash';
import { AppLoadingContext } from '@/app/context/AppLoadingContext';
import * as Font from 'expo-font';
import Entypo from '@expo/vector-icons/Entypo';

// Get screen width to calculate relative sizes
const [screenWidth, screenHeight] = [Dimensions.get('window').width, Dimensions.get('window').height];
const tabBarWidth = screenWidth * 0.5; // Adjust this multiplier to change width
const tabBarHeight = screenHeight * 0.05 // Adjust multiplier to change height

export default function TabLayout() {
  const [appIsReady, setAppIsReady] = useState(false);
  const [isExistingUser, setIsExistingUser] = useState(false);
  const router = useRouter();

  useEffect(() => {
    async function prepare() {
      try {
        await Font.loadAsync(Entypo.font);
        // Simulate user check
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (e) {
        console.warn(e);
      } finally {
        setAppIsReady(true);
        if (isExistingUser) {
          router.replace('/');
        }
      }
    }
    prepare();
  }, [isExistingUser]);

  return (
    <AppLoadingContext.Provider value={{ appIsReady, setAppIsReady }}>
      {(!appIsReady) ? (
        <SplashScreen />
      ) : (!isExistingUser && appIsReady) ? (
        <Onboarding onSubmit={() => {
          setIsExistingUser(true);
        }} />
      ) : (
        <Tabs screenOptions={{ 
            tabBarActiveTintColor: Colours.light.accent, 
            tabBarStyle: { 
              // Hide tab bar when app is not ready
              display: appIsReady ? 'flex' : 'none',
              // position: 'absolute',
              bottom: 40,
              width: tabBarWidth,
              alignSelf: 'center',
              height: tabBarHeight,
              borderRadius: 30,
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              shadowColor: "#000",
              shadowOffset: {
                width: 0,
                height: 2,
              },
              shadowOpacity: 0.25,
              shadowRadius: 3.84,
              elevation: 5,
              borderTopWidth: 0,
              marginHorizontal: 'auto',
              paddingTop: 2
            }, 
            tabBarBackground: () => (
              <BlurView tint="light" intensity={50} style={[StyleSheet.absoluteFill,
                { 
                  borderRadius: 30,
                  overflow: 'hidden',
                }]
              } />
            ),
            tabBarItemStyle: {
              padding: 0,
            },
          }}>
          <Tabs.Screen
            name="index"
            options={{
              title: "",
              tabBarIcon: ({ color }) => <FontAwesome size={24} name="home" color={color} />,
              headerShown: false
            }}
          />
          <Tabs.Screen
            name="test"
            options={{
              title: "",
              tabBarIcon: ({ color }) => <FontAwesome size={20} name="search" color={color} />,
              headerShown: false
            }}
          />
          {/* <Tabs.Screen
            name="stays"
            options={{
              title: "",
              tabBarIcon: ({ color }) => <FontAwesome size={20} name="map" color={color} />,
              headerShown: false
            }}
          /> */}
        </Tabs>
      )}
    </AppLoadingContext.Provider>
  );
}