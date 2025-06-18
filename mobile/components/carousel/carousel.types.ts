import { ImageSourcePropType } from "react-native";

export type CarouselItem = {
    img: ImageSourcePropType;
    name: string;
    onPress?: () => void;
};
