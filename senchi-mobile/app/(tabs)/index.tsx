import { Colours } from '@/constants/colours';
import { Header } from '@react-navigation/elements';
import { Link } from 'expo-router';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView,
  ActivityIndicator,
  ImageURISource,
  Pressable,
  ViewToken,
} from 'react-native';
import Animated, { 
  useAnimatedRef,
  useAnimatedScrollHandler,
  useSharedValue,
} from 'react-native-reanimated';
import { useCallback } from 'react';
import ListItem from '@/components/ListItem';
import PaginationElement from '@/components/PaginationElement';
import Button from '@/components/Button';


export default function HomeScreen() {
  
  return (
   <SafeAreaView style={styles.container}>
      <Text>Home</Text>
  </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  bottomContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
});
