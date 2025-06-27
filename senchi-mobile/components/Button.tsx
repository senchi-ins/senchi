import {
    ImageURISource,
    Pressable,
    StyleSheet,
    Text,
    View,
  } from 'react-native';
  import React, { useCallback } from 'react';
  import Animated, {
    useAnimatedStyle,
    withSpring,
    withTiming,
    SharedValue,
  } from 'react-native-reanimated';
  
  type Props = {
    currentIndex: SharedValue<number>;
    length: number;
    flatListRef: any;
    onSubmit: () => void;
  };
  const AnimatedPressable = Animated.createAnimatedComponent(Pressable);
  
  const Button = ({ currentIndex, length, flatListRef, onSubmit }: Props) => {
    const rnBtnStyle = useAnimatedStyle(() => {
      return {
        width:
          currentIndex.value === length - 1 ? withSpring(140) : withSpring(60),
        height: 60,
      };
    }, [currentIndex, length]);
  
    const rnTextStyle = useAnimatedStyle(() => {
      return {
        opacity:
          currentIndex.value === length - 1 ? withTiming(1) : withTiming(0),
        transform: [
          {
            translateX:
              currentIndex.value === length - 1 ? withTiming(0) : withTiming(100),
          },
        ],
      };
    }, [currentIndex, length]);
  
    const imageAnimatedStyle = useAnimatedStyle(() => {
      return {
        opacity:
          currentIndex.value !== length - 1 ? withTiming(1) : withTiming(0),
        transform: [
          {
            translateX:
              currentIndex.value !== length - 1 ? withTiming(0) : withTiming(100),
          },
        ],
      };
    }, [currentIndex, length]);
  
    const onPress = useCallback(() => {
      if (currentIndex.value === length - 1) {
        onSubmit();
      } else {
        flatListRef?.current?.scrollToIndex({
          index: currentIndex.value + 1,
        });
      }
    }, []);
    return (
      <AnimatedPressable style={[styles.container, rnBtnStyle]} onPress={onPress}>
        <Animated.Text style={[styles.textStyle, rnTextStyle]}>
          Get Started
        </Animated.Text>
        <Animated.Image
          source={require('@/assets/images/arrow_right.png')}
          style={[styles.imageStyle, imageAnimatedStyle]}
        />
      </AnimatedPressable>
    );
  };
  
  export default Button;
  
  const styles = StyleSheet.create({
    container: {
      flexDirection: 'row',
      paddingHorizontal: 24,
      paddingVertical: 16,
      borderRadius: 100,
      backgroundColor: '#240DBF',
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden',
    },
    textStyle: {
      color: 'white',
      position: 'absolute',
      fontWeight: '600',
      fontSize: 16,
    },
    imageStyle: {
      width: 24,
      height: 24,
      position: 'absolute',
      tintColor: 'white',
    },
  });