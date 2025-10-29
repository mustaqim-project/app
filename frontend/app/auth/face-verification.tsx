import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { authAPI } from '../../services/api';

export default function FaceVerificationScreen() {
  const [selfie, setSelfie] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const { refreshUser } = useAuth();
  const router = useRouter();

  const takeSelfie = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Mohon izinkan akses ke kamera');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.5,
      base64: true,
    });

    if (!result.canceled && result.assets[0].base64) {
      setSelfie(result.assets[0].base64);
    }
  };

  const handleVerify = async () => {
    if (!selfie) {
      Alert.alert('Error', 'Silakan ambil foto selfie terlebih dahulu');
      return;
    }

    setLoading(true);
    try {
      const response = await authAPI.verifyFace(selfie);
      if (response.data.verified) {
        Alert.alert('Sukses', 'Wajah berhasil diverifikasi!', [
          {
            text: 'OK',
            onPress: async () => {
              await refreshUser();
              router.replace('/auth/assessment');
            },
          },
        ]);
      } else {
        Alert.alert('Gagal', 'Verifikasi wajah gagal. Silakan coba lagi.');
        setSelfie('');
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Verifikasi gagal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Ionicons name="scan" size={80} color="#FF6B9D" />
        <Text style={styles.title}>Verifikasi Wajah</Text>
        <Text style={styles.subtitle}>Ambil foto selfie untuk verifikasi</Text>
      </View>

      {selfie ? (
        <View style={styles.previewContainer}>
          <Image
            source={{ uri: `data:image/jpeg;base64,${selfie}` }}
            style={styles.preview}
          />
          <TouchableOpacity style={styles.retakeButton} onPress={takeSelfie}>
            <Ionicons name="camera" size={24} color="#FFF" />
            <Text style={styles.retakeButtonText}>Ambil Ulang</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <TouchableOpacity style={styles.cameraButton} onPress={takeSelfie}>
          <Ionicons name="camera" size={60} color="#FFF" />
          <Text style={styles.cameraButtonText}>Ambil Foto</Text>
        </TouchableOpacity>
      )}

      <TouchableOpacity
        style={[styles.button, !selfie && styles.buttonDisabled]}
        onPress={handleVerify}
        disabled={!selfie || loading}
      >
        {loading ? (
          <ActivityIndicator color="#FFF" />
        ) : (
          <Text style={styles.buttonText}>Verifikasi</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF0F5',
    padding: 24,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FF6B9D',
    marginTop: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
  previewContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  preview: {
    width: 250,
    height: 250,
    borderRadius: 125,
    marginBottom: 16,
  },
  retakeButton: {
    flexDirection: 'row',
    backgroundColor: '#666',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    gap: 8,
  },
  retakeButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  cameraButton: {
    backgroundColor: '#FF6B9D',
    height: 200,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 32,
  },
  cameraButtonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 12,
  },
  button: {
    backgroundColor: '#FF6B9D',
    borderRadius: 12,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#CCC',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
});