import * as React from "react";
import { Dimensions, View, Image, Pressable, Animated } from "react-native";
import { interpolate } from "react-native-reanimated";
import Carousel, { TAnimationStyle } from "react-native-reanimated-carousel";
import * as Haptics from 'expo-haptics';

import { CarouselItem } from "./carousel.types";

const PAGE_WIDTH = Dimensions.get("window").width;
const PAGE_HEIGHT = Dimensions.get("window").height * 0.25;

function MobileCarousel({ items, onIndexChange }:  { 
	items: CarouselItem[], onIndexChange: (index: number) => void 
}) {
	const itemSize = 150;
  	const itemOpacity = 0.5;
	const centerOffset = PAGE_WIDTH / 2 - itemSize / 2;
	const [currentIndex, setCurrentIndex] = React.useState(0);

	// Animated opacity values for each item
	const animatedOpacities = React.useRef(
    items.map((_, i) => new Animated.Value(i === 0 ? 1 : itemOpacity)),
  ).current;

	React.useEffect(() => {
		animatedOpacities.forEach((opacity, i) => {
			Animated.timing(opacity, {
				toValue: i === currentIndex ? 1 : itemOpacity,
				duration: 200,
				useNativeDriver: true,
			}).start();
		});
	}, [currentIndex, animatedOpacities]);

	const animationStyle: TAnimationStyle = React.useCallback(
		(value: number) => {
			"worklet";

			const itemGap = interpolate(
				value,
				[-3, -2, -1, 0, 1, 2, 3],
				[-3, -2, -1, 0, 1, 2, 3],
			);

			const translateX =
				interpolate(value, [-1, 0, 1], [-itemSize, 0, itemSize]) +
				centerOffset -
				itemGap;

			const translateY = interpolate(
				value,
				[-1, -0.5, 0, 0.5, 1],
				[60, 45, 40, 45, 60],
			);

			const scale = interpolate(
				value,
				[-1, -0.5, 0, 0.5, 1],
				[0.8, 0.85, 1.1, 0.85, 0.8],
			);

			return {
				transform: [
					{
						translateX,
					},
					{
						translateY,
					},
					{ scale },
				],
			};
		},
		[centerOffset],
	);

	return (
		<View style={{ paddingVertical: 0, width: '100%' }}>
			<View style={{ alignItems: 'center', marginBottom: 0 }}>
				{items[currentIndex]?.name && (
					<Animated.Text 
          style={{ 
            fontSize: 20, 
            fontWeight: 'bold', 
            opacity: animatedOpacities[currentIndex],
            fontFamily: 'Poppins_400Regular'
          }}>
						{`My ${items[currentIndex].name}`}
					</Animated.Text>
				)}
			</View>
			<Carousel
				width={itemSize}
				height={itemSize}
				style={{
					width: PAGE_WIDTH,
					height: PAGE_HEIGHT,
					marginBottom: 16,
				}}
				loop
				data={items}
				renderItem={({ index }) => (
					<Pressable
						key={index}
						onPress={() => {
							Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
							console.log(index);
						}}
						style={{ flex: 1 }}
					>
						<Animated.View
							style={{
								flex: 1,
								borderRadius: 50,
								justifyContent: "center",
								overflow: "hidden",
								alignItems: "center",
								opacity: animatedOpacities[index],
							}}
						>
							<Image
								source={items[index].img}
								style={{ width: itemSize, height: itemSize, borderRadius: 50 }}
								resizeMode="cover"
							/>
						</Animated.View>
					</Pressable>
				)}
				customAnimation={animationStyle}
				onSnapToItem={index => {
					setCurrentIndex(index);
					onIndexChange(index);
					Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
				}}
			/>
		</View>
	);
}

export default MobileCarousel;