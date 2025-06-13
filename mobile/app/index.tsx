import { useState } from "react";
import { SafeAreaView, View } from "react-native";
import Header from "../components/header";
import MobileCarousel from "../components/carousel";
import { CarouselItem } from "../components/carousel/carousel.types";
import Button from "../components/button";
import Included from "@/components/included";


const images: CarouselItem[] = [
  { img: require("../assets/gend/car.png"), name: "Car" },
  { img: require("../assets/gend/condo.png"), name: "Apartment" },
  { img: require("../assets/gend/home.png"), name: "Home" },
];

export default function Index() {
  const [selectedIndex, setSelectedIndex] = useState(0);
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fafafa" }}>
      <Header />
      <View style={{ flex: 1, justifyContent: "flex-start" }}>
        <MobileCarousel items={images} onIndexChange={setSelectedIndex} />
        <Included selectedIndex={selectedIndex} />
      </View>
      <View style={{ alignItems: "center", marginBottom: 32 }}>
        <Button text="Start your quote" onPress={() => {}} />
      </View>
    </SafeAreaView>
  );
}
