# Flutter Mobile App

Project-specific guidance for Flutter applications.

---

## 🔍 Detection

Auto-detected when `pubspec.yaml` exists.

---

## 🛠️ Commands

```bash
flutter run              # Run app
flutter test            # Run tests
flutter analyze         # Lint/analyze code
flutter build apk       # Build Android
flutter build ios       # Build iOS
flutter clean           # Clean build artifacts
dart format .           # Format code
```

---

## 📁 Common Structure

```
project/
├── lib/
│   ├── main.dart
│   ├── screens/
│   │   ├── home_screen.dart
│   │   └── profile_screen.dart
│   ├── widgets/
│   │   ├── custom_button.dart
│   │   └── user_card.dart
│   ├── services/
│   │   └── api_service.dart
│   ├── models/
│   │   └── user.dart
│   ├── providers/
│   │   └── auth_provider.dart
│   └── utils/
│       └── validators.dart
├── test/
│   └── widget_test.dart
├── assets/
│   ├── images/
│   └── fonts/
└── pubspec.yaml
```

---

## ⚙️ Flutter Patterns

### Main Entry Point

```dart
// lib/main.dart
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomeScreen(),
    );
  }
}
```

### Screen Widget

```dart
// lib/screens/home_screen.dart
import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Home'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('You have pushed the button this many times:'),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

### API Service

```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'https://api.example.com';

  Future<List<User>> getUsers() async {
    final response = await http.get(Uri.parse('$baseUrl/users'));

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => User.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load users');
    }
  }

  Future<User> createUser(User user) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(user.toJson()),
    );

    if (response.statusCode == 201) {
      return User.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to create user');
    }
  }
}
```

### Model

```dart
// lib/models/user.dart
class User {
  final String id;
  final String name;
  final String email;

  const User({
    required this.id,
    required this.name,
    required this.email,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      name: json['name'] as String,
      email: json['email'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
    };
  }
}
```

---

## 🧪 Testing

```dart
// test/widget_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:myapp/main.dart';

void main() {
  testWidgets('Counter increments smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('0'), findsOneWidget);
    expect(find.text('1'), findsNothing);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pump();

    expect(find.text('0'), findsNothing);
    expect(find.text('1'), findsOneWidget);
  });
}
```

---

## 🔧 Environment Configuration

```yaml
# pubspec.yaml
name: myapp
description: My Flutter app

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0
```

---

## ✅ Quality Gates

- [ ] `flutter analyze` passes
- [ ] `flutter test` passes
- [ ] Code formatted (`dart format .`)
- [ ] No deprecated API usage
- [ ] Runs on iOS
- [ ] Runs on Android
- [ ] Proper error handling
- [ ] Images optimized

---

## 🚀 Build & Deploy

**Android:**
```bash
flutter build apk --release
flutter build appbundle --release
```

**iOS:**
```bash
flutter build ios --release
```

**Web:**
```bash
flutter build web
```

---

**Reference:** https://flutter.dev/docs
