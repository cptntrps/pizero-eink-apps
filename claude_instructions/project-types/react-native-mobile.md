# React Native Mobile App

Project-specific guidance for React Native applications.

---

## 🔍 Detection

Auto-detected when `package.json` contains `"react-native"` dependency.

---

## 🛠️ Commands

```bash
# Development
npm start              # Start Metro bundler
npm run ios           # Run iOS simulator
npm run android       # Run Android emulator
npm run web           # Run web (Expo)

# Testing
npm test
npm run test:watch

# Linting
npm run lint
npm run lint -- --fix

# Type checking
npm run typecheck
```

---

## 📁 Common Structure

```
project/
├── src/
│   ├── screens/
│   │   ├── HomeScreen.tsx
│   │   └── ProfileScreen.tsx
│   ├── components/
│   │   ├── Button.tsx
│   │   └── Card.tsx
│   ├── navigation/
│   │   └── AppNavigator.tsx
│   ├── services/
│   │   └── api.ts
│   ├── hooks/
│   │   └── useAuth.ts
│   ├── context/
│   │   └── AuthContext.tsx
│   ├── utils/
│   │   └── validation.ts
│   └── types/
│       └── index.ts
├── assets/
│   ├── images/
│   └── fonts/
├── __tests__/
├── App.tsx
└── package.json
```

---

## ⚙️ React Native Patterns

### Screen Component

```tsx
// src/screens/HomeScreen.tsx
import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { useQuery } from '@tanstack/react-query';

export function HomeScreen() {
  const { data, isLoading } = useQuery(['posts'], fetchPosts);

  if (isLoading) {
    return <Text>Loading...</Text>;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Home</Text>
      <FlatList
        data={data}
        renderItem={({ item }) => <PostCard post={item} />}
        keyExtractor={item => item.id}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
});
```

### Navigation (React Navigation)

```tsx
// src/navigation/AppNavigator.tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { HomeScreen } from '../screens/HomeScreen';
import { ProfileScreen } from '../screens/ProfileScreen';

const Stack = createNativeStackNavigator();

export function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Profile" component={ProfileScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### API Service

```typescript
// src/services/api.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.EXPO_PUBLIC_API_URL;

async function getAuthToken() {
  return await AsyncStorage.getItem('authToken');
}

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = await getAuthToken();

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
```

---

## 🧪 Testing

```tsx
// __tests__/Button.test.tsx
import { render, fireEvent } from '@testing-library/react-native';
import { Button } from '../src/components/Button';

describe('Button', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Button title="Click me" />);
    expect(getByText('Click me')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const onPress = jest.fn();
    const { getByText } = render(<Button title="Click" onPress={onPress} />);

    fireEvent.press(getByText('Click'));
    expect(onPress).toHaveBeenCalledTimes(1);
  });
});
```

---

## 🔧 Environment Variables (Expo)

```bash
# .env
EXPO_PUBLIC_API_URL=https://api.example.com
```

Access with:
```typescript
const apiUrl = process.env.EXPO_PUBLIC_API_URL;
```

---

## ✅ Quality Gates

- [ ] Tests pass
- [ ] Linting passes
- [ ] TypeScript compiles
- [ ] Runs on iOS simulator
- [ ] Runs on Android emulator
- [ ] No console warnings
- [ ] Images optimized
- [ ] Proper error handling

---

## 📱 Platform-Specific Code

```tsx
import { Platform, StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    padding: Platform.select({
      ios: 16,
      android: 12,
      default: 16,
    }),
  },
});

// Or separate files
import Button from './Button.ios';  // iOS
import Button from './Button.android'; // Android
```

---

## 🚀 Build & Deploy

**Expo:**
```bash
# Build
eas build --platform ios
eas build --platform android

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

**React Native CLI:**
```bash
# iOS
cd ios && pod install && cd ..
npx react-native run-ios

# Android
npx react-native run-android
```

---

**Reference:** https://reactnative.dev/
