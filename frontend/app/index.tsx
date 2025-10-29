import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';

export default function Index() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.replace('/auth/login');
      } else if (!user.verified_face) {
        router.replace('/auth/face-verification');
      } else if (!user.assessments_completed) {
        router.replace('/auth/assessment');
      } else {
        router.replace('/tabs');
      }
    }
  }, [user, loading]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#FF6B9D" />
      <Text style={styles.text}>Memuat...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFF0F5',
  },
  text: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
});