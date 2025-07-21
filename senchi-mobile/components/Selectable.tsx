import React from 'react';
import { View, Text, StyleSheet, Pressable, ImageSourcePropType, Image } from 'react-native';

interface SelectableProps {
  children: React.ReactNode;
  selected: boolean;
  image?: ImageSourcePropType;
  onSelect: () => void;
}

export const Selectable = ({ children, selected, image, onSelect }: SelectableProps) => {
  return (
    <Pressable onPress={onSelect} style={styles.container}>
      <View style={[styles.container, selected ? styles.selected : styles.unselected]}>
        {image && <Image source={image} style={styles.image} />}
        <Text style={[styles.text, selected ? styles.selectedText : styles.unselectedText]} numberOfLines={1}>{children}</Text>
      </View>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 0,
    paddingHorizontal: 20,
    borderRadius: 8,
    width: '95%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-start',
    gap: 12,
    alignSelf: 'center',
    marginVertical: 4,
    minHeight: 56,
  },
  selected: {
    backgroundColor: '#240DBF',
    color: 'white',
  },
  unselected: {
    backgroundColor: '#E5E7EB', // gray-200
  },
  text: {
    fontSize: 18,
    fontWeight: '500',
    color: '#000',
    flex: 1,
    marginLeft: 8,
  },
  image: {
    width: 50,
    height: 50,
  },
  selectedText: {
    color: 'white',
  },
  unselectedText: {
    color: '#000',
  },
});
