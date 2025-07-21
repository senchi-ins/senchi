import React, { useEffect, useRef } from 'react';
import { Animated, Easing, View, StyleSheet, Image } from 'react-native';
import LottieView from 'lottie-react-native';

const AnimatedLottieView = Animated.createAnimatedComponent(LottieView);

export default function SplashScreen() {
  const animationProgress = useRef(new Animated.Value(0));

  useEffect(() => {
    Animated.timing(animationProgress.current, {
      toValue: 1,
      duration: 5000,
      easing: Easing.linear,
      useNativeDriver: false,
    }).start();
  }, []);

  return (
    <View style={styles.container}>
      {/* <AnimatedLottieView
        source={require('../assets/animations/Lottie_Lego.json')}
        progress={animationProgress.current}
        style={styles.animation}
      /> */}
      <Image 
        alt="Senchi Logo" 
        source={require('../assets/images/senchi.png')} 
        style={styles.image} 
        resizeMode="contain"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#240DBF',
  },
  animation: {
    width: 200,
    height: 200,
  },
  image: {
    width: 200,
    height: 200,
  },
});