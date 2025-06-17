import { useState } from "react";
import { SafeAreaView, View } from "react-native";
import Header from "../components/header";
import MobileCarousel from "../components/carousel";
import { CarouselItem } from "../components/carousel/carousel.types";
import Button from "../components/button";
import Included from "@/components/included";
import { Callout } from "@/components/callout";
import callouts from "@/components/callout/callouts";
import { router } from "expo-router";


const images: CarouselItem[] = [
  { img: require("../assets/gend/home.png"), name: "Apartment 2" },
  { img: require("../assets/gend/condo.png"), name: "Toronto Apartment" },
  { img: require("../assets/gend/home.png"), name: "Whitby Home" },
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
      <Callout callout={callouts[selectedIndex]} />
      <View style={{ alignItems: "center", marginBottom: 32 }}>
        <Button text="Start your assessment" onPress={() => {
          console.log("Start your assessment")
          router.push({
            pathname: "/quote",
            params: {
              selectedInsurance: images[selectedIndex].name,
            },
          })
        }} />
      </View>
    </SafeAreaView>
  );
}
