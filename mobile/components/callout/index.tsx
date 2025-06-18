import * as React from 'react'
import { View, Text } from 'react-native'
import { CalloutProps } from './callout.types'
import { Colours } from '@/constants/colors'

export const Callout = ({ callout }: CalloutProps) => {
    return (
        <View>
            <Text 
            style={{
                fontSize: 16,
                fontWeight: 'bold',
                color: Colours.light.primary,
                textAlign: 'center',
                marginHorizontal: 16,
                marginBottom: 24,
            }}
            >
                {callout}
            </Text>
        </View>
  )
}