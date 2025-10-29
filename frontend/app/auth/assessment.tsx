import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { assessmentAPI } from '../../services/api';

const TEST_TYPES = [
  { id: 'mbti', title: 'MBTI', description: 'Tes Kepribadian' },
  { id: 'love_language', title: 'Love Language', description: 'Bahasa Cinta' },
  { id: 'readiness', title: 'Readiness', description: 'Kesiapan Hubungan' },
  { id: 'temperament', title: 'Temperament', description: 'Temperamen' },
  { id: 'disc', title: 'DISC', description: 'Profil Perilaku' },
];

export default function AssessmentScreen() {
  const [currentTest, setCurrentTest] = useState<string | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [completedTests, setCompletedTests] = useState<string[]>([]);
  const { refreshUser } = useAuth();
  const router = useRouter();

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const response = await assessmentAPI.getStatus();
      const completed = [];
      if (response.data.mbti) completed.push('mbti');
      if (response.data.love_language) completed.push('love_language');
      if (response.data.readiness > 0) completed.push('readiness');
      if (response.data.temperament) completed.push('temperament');
      if (response.data.disc) completed.push('disc');
      setCompletedTests(completed);

      if (response.data.all_completed) {
        router.replace('/tabs');
      }
    } catch (error) {
      console.error('Check status error:', error);
    }
  };

  const startTest = async (testType: string) => {
    setLoading(true);
    try {
      const response = await assessmentAPI.getQuestions(testType);
      setQuestions(response.data.questions);
      setCurrentTest(testType);
      setCurrentQuestion(0);
      setAnswers([]);
    } catch (error: any) {
      Alert.alert('Error', 'Gagal memuat pertanyaan');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (answerIndex: number) => {
    const newAnswers = [...answers, answerIndex];
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      submitTest(newAnswers);
    }
  };

  const submitTest = async (finalAnswers: number[]) => {
    setLoading(true);
    try {
      const response = await assessmentAPI.submitAnswers(currentTest!, finalAnswers);
      
      Alert.alert(
        'Tes Selesai!',
        `Hasil: ${JSON.stringify(response.data.result)}`,
        [
          {
            text: 'OK',
            onPress: () => {
              setCurrentTest(null);
              setQuestions([]);
              setCurrentQuestion(0);
              setAnswers([]);
              checkStatus();
            },
          },
        ]
      );
    } catch (error: any) {
      Alert.alert('Error', 'Gagal mengirim jawaban');
    } finally {
      setLoading(false);
    }
  };

  if (currentTest && questions.length > 0) {
    const question = questions[currentQuestion];
    return (
      <View style={styles.container}>
        <View style={styles.progressContainer}>
          <Text style={styles.progressText}>
            {currentQuestion + 1} / {questions.length}
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${((currentQuestion + 1) / questions.length) * 100}%` },
              ]}
            />
          </View>
        </View>

        <ScrollView contentContainerStyle={styles.questionContainer}>
          <Text style={styles.questionText}>{question.question}</Text>

          {question.options.map((option: string, index: number) => (
            <TouchableOpacity
              key={index}
              style={styles.optionButton}
              onPress={() => handleAnswer(index)}
              disabled={loading}
            >
              <Text style={styles.optionText}>{option}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="clipboard" size={80} color="#FF6B9D" />
        <Text style={styles.title}>Asesmen Wajib</Text>
        <Text style={styles.subtitle}>
          Selesaikan 5 asesmen untuk menggunakan aplikasi
        </Text>
      </View>

      <ScrollView contentContainerStyle={styles.testList}>
        {TEST_TYPES.map((test) => {
          const isCompleted = completedTests.includes(test.id);
          return (
            <TouchableOpacity
              key={test.id}
              style={[
                styles.testCard,
                isCompleted && styles.testCardCompleted,
              ]}
              onPress={() => !isCompleted && startTest(test.id)}
              disabled={isCompleted || loading}
            >
              <View style={styles.testCardContent}>
                <View>
                  <Text style={styles.testTitle}>{test.title}</Text>
                  <Text style={styles.testDescription}>{test.description}</Text>
                </View>
                {isCompleted ? (
                  <Ionicons name="checkmark-circle" size={32} color="#4CAF50" />
                ) : (
                  <Ionicons name="arrow-forward" size={32} color="#FF6B9D" />
                )}
              </View>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {completedTests.length === 5 && (
        <TouchableOpacity
          style={styles.continueButton}
          onPress={() => router.replace('/tabs')}
        >
          <Text style={styles.continueButtonText}>Lanjutkan</Text>
        </TouchableOpacity>
      )}

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#FF6B9D" />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF0F5',
  },
  header: {
    alignItems: 'center',
    padding: 24,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FF6B9D',
    marginTop: 16,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
  testList: {
    padding: 24,
  },
  testCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  testCardCompleted: {
    backgroundColor: '#E8F5E9',
  },
  testCardContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  testTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  testDescription: {
    fontSize: 14,
    color: '#666',
  },
  progressContainer: {
    padding: 24,
    paddingTop: 60,
  },
  progressText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FF6B9D',
    marginBottom: 8,
    textAlign: 'center',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#FF6B9D',
  },
  questionContainer: {
    padding: 24,
  },
  questionText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginBottom: 24,
    textAlign: 'center',
  },
  optionButton: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  optionText: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
  },
  continueButton: {
    backgroundColor: '#FF6B9D',
    borderRadius: 12,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
    margin: 24,
  },
  continueButtonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
});