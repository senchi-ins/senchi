import { Colours } from '@/constants/colours';
import { Header } from '@react-navigation/elements';
import { useRouter } from 'expo-router';
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
import SplashScreen from '@/animations/splash';
import { useCallback, useEffect } from 'react';
import Entypo from '@expo/vector-icons/Entypo';
import * as Font from 'expo-font';
import { useAppLoading } from '@/app/context/AppLoadingContext';
import { useExistingUser } from '@/app/context/ExistingUser';
import ListItem from '@/components/ListItem';
import PaginationElement from '@/components/PaginationElement';
import Button from '@/components/Button';

const pages = [
  {
    "text": "Welcome to Senchi",
    "image": require('@/assets/gend/car.png'),
  },
  {
    "text": "What do you use?",
    "image": require('@/assets/gend/car.png'),
  },
  {
    "text": "Get started",
    "image": require('@/assets/gend/car.png'),
  }
]

type Props = {
  onSubmit: () => void;
}

export default function HomeScreen({ onSubmit }: Props) {
  const router = useRouter();
  const x = useSharedValue(0);
  const flatListIndex = useSharedValue(0);
  const flatListRef = useAnimatedRef<Animated.FlatList<{
    text: string;
    image: ImageURISource;
  }>>();
  const onViewableItemsChanged = useCallback(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      flatListIndex.value = viewableItems[0].index ?? 0;
    },
    []
  );

  const scrollHandle = useAnimatedScrollHandler({
    onScroll: (event) => {
      x.value = event.contentOffset.x;
    }
  })

  const renderItem = useCallback(
    ({ 
      item,
      index,
     }: { 
      item: { text: string; image: ImageURISource }, 
      index: number }) => {
        return <ListItem item={item} index={index} x={x} />
      },
      [x]
  );
  const { appIsReady, setAppIsReady } = useAppLoading();
  const { isExistingUser, setIsExistingUser } = useExistingUser();
  useEffect(() => {
    async function prepare() {
      try {
        // Pre-load fonts, make any API calls you need to do here
        await Font.loadAsync(Entypo.font);
        // Artificially delay for four seconds to simulate a slow loading
        // experience. Remove this if you copy and paste the code!
        await new Promise(resolve => setTimeout(resolve, 4000));
      } catch (e) {
        console.warn(e);
      } finally {
        // Tell the application to render
        setAppIsReady(true);
      }
    }

    prepare();
  }, [setAppIsReady]);

  const onLayoutRootView = useCallback(() => {
    if (appIsReady) {
      // This callback is called when the app is ready
    }
  }, [appIsReady]);

  // Show splash screen while app is loading
  if (!appIsReady) {
    return <SplashScreen />;
  }

  // Show main content when app is ready
  return (

    <SafeAreaView style={styles.container}>
      <Animated.FlatList
        ref={flatListRef}
        onScroll={scrollHandle}
        horizontal
        scrollEventThrottle={16}
        pagingEnabled={true}
        data={pages}
        keyExtractor={(_, index) => index.toString()}
        bounces={false}
        renderItem={renderItem}
        showsHorizontalScrollIndicator={false}
        onViewableItemsChanged={onViewableItemsChanged}
      />
      <View style={styles.bottomContainer}>
        <PaginationElement length={pages.length} x={x} />
        <Button
          currentIndex={flatListIndex}
          length={pages.length}
          flatListRef={flatListRef}
          onSubmit={() => {
            onSubmit();
          }}
        />
      </View>
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

