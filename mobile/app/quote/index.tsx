import { useState, useRef } from "react";
import { SafeAreaView, View, Text, TextInput, ScrollView, KeyboardAvoidingView, Platform, TouchableOpacity, Pressable, Animated } from "react-native";
import Header from "@/components/header";
import { useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Colours } from "@/constants/colors";
import { script, beneficialItems, liveWith } from "./script";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  options?: string[];
  selectedOptions?: string[];
}

export default function Quote() {
  const { selectedInsurance } = useLocalSearchParams();
  const [currentStep, setCurrentStep] = useState(0);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: `Welcome! I'll help you get a quote for your ${selectedInsurance}. To start, what's your address?`,
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [showOptions, setShowOptions] = useState(false);
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const scrollViewRef = useRef<ScrollView>(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;

  const animateNewMessage = () => {
    fadeAnim.setValue(0);
    slideAnim.setValue(20);
    
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const handleOptionSelect = (option: string) => {
    const newSelectedOptions = selectedOptions.includes(option)
      ? selectedOptions.filter(item => item !== option)
      : [...selectedOptions, option];
    
    setSelectedOptions(newSelectedOptions);
    
    // For Yes/No questions, send immediately
    if (script[currentStep].options.length === 2) {
      handleSend(newSelectedOptions);
    }
  };

  const handleSend = (optionsToSend: string[] = selectedOptions) => {
    if (inputText.trim() === "" && optionsToSend.length === 0) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      text: inputText || optionsToSend.join(", "),
      isUser: true,
      timestamp: new Date(),
      selectedOptions: optionsToSend,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputText("");
    setSelectedOptions([]);
    setShowOptions(false);
    animateNewMessage();

    // Process next step
    setTimeout(() => {
      const nextStep = currentStep + 1;
      setCurrentStep(nextStep);
      
      if (nextStep < script.length) {
        const nextQuestion = script[nextStep];
        
        const agentResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: nextQuestion.question,
          isUser: false,
          timestamp: new Date(),
          options: nextQuestion.options,
        };
        
        setMessages((prev) => [...prev, agentResponse]);
        if (nextQuestion.options) {
          setShowOptions(true);
        }
        animateNewMessage();
      }
    }, 1000);
  };

  const renderOptions = (options: string[]) => {
    return (
      <Animated.View 
        style={{ 
          flexDirection: 'row', 
          flexWrap: 'wrap', 
          gap: 8, 
          marginTop: 8,
          opacity: fadeAnim,
          transform: [{ translateY: slideAnim }]
        }}
      >
        {options.map((option) => (
          <Pressable
            key={option}
            onPress={() => handleOptionSelect(option)}
            style={{
              backgroundColor: selectedOptions.includes(option) ? Colours.light.primary : '#E5E5EA',
              paddingHorizontal: 16,
              paddingVertical: 8,
              borderRadius: 20,
              borderWidth: 1,
              borderColor: selectedOptions.includes(option) ? Colours.light.primary : '#E5E5EA',
            }}
          >
            <Text
              style={{
                color: selectedOptions.includes(option) ? '#FFFFFF' : '#000000',
                fontSize: 14,
              }}
            >
              {option}
            </Text>
          </Pressable>
        ))}
      </Animated.View>
    );
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fafafa" }}>
      <Header />
      <KeyboardAvoidingView 
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={{ flex: 1 }}
      >
        <ScrollView 
          ref={scrollViewRef}
          style={{ flex: 1 }}
          contentContainerStyle={{ padding: 16 }}
          onContentSizeChange={() => scrollViewRef.current?.scrollToEnd({ animated: true })}
        >
          {messages.map((message, index) => (
            <Animated.View 
              key={message.id}
              style={{
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }]
              }}
            >
              <View
                style={{
                  alignSelf: message.isUser ? "flex-end" : "flex-start",
                  backgroundColor: message.isUser ? Colours.light.primary : "#E5E5EA",
                  padding: 12,
                  borderRadius: 16,
                  maxWidth: "80%",
                  marginBottom: 8,
                }}
              >
                <Text
                  style={{
                    color: message.isUser ? "#FFFFFF" : "#000000",
                    fontSize: 16,
                  }}
                >
                  {message.text}
                </Text>
              </View>
              {message.options && !message.isUser && renderOptions(message.options)}
            </Animated.View>
          ))}
        </ScrollView>
        
        <View
          style={{
            flexDirection: "row",
            padding: 16,
            borderTopWidth: 1,
            borderTopColor: "#E5E5EA",
            backgroundColor: "#FFFFFF",
          }}
        >
          {!showOptions && (
            <TextInput
              style={{
                flex: 1,
                backgroundColor: "#F2F2F7",
                borderRadius: 20,
                paddingHorizontal: 16,
                paddingVertical: 8,
                marginRight: 8,
                fontSize: 16,
              }}
              placeholder="Type your message..."
              value={inputText}
              onChangeText={setInputText}
              multiline
            />
          )}
          {!showOptions && (
            <TouchableOpacity
              onPress={() => handleSend()}
              style={{
                backgroundColor: Colours.light.primary,
                width: 40,
                height: 40,
                borderRadius: 20,
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <Ionicons name="send" size={20} color="#FFFFFF" />
            </TouchableOpacity>
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}