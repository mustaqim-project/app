import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  ActivityIndicator,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';

export default function RegisterScreen() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    date_of_birth: '',
    gender: 'male',
    username: '',
    profile_photo: '',
    latitude: 0,
    longitude: 0,
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Mohon izinkan akses ke galeri foto');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.5,
      base64: true,
    });

    if (!result.canceled && result.assets[0].base64) {
      setFormData({ ...formData, profile_photo: result.assets[0].base64 });
    }
  };

  const getLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Required', 'Mohon izinkan akses lokasi');
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setFormData({
        ...formData,
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
      });
      Alert.alert('Success', 'Lokasi berhasil didapat');
    } catch (error) {
      Alert.alert('Error', 'Gagal mendapatkan lokasi');
    }
  };

  const handleRegister = async () => {
    if (!formData.name || !formData.email || !formData.password || !formData.username) {
      Alert.alert('Error', 'Silakan isi semua field yang wajib');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Password tidak cocok');
      return;
    }

    if (!formData.profile_photo) {
      Alert.alert('Error', 'Silakan pilih foto profil');
      return;
    }

    if (formData.latitude === 0 || formData.longitude === 0) {
      Alert.alert('Error', 'Silakan aktifkan lokasi');
      return;
    }

    setLoading(true);
    try {
      await register(formData);
      // Navigation will be handled by index.tsx
    } catch (error: any) {
      Alert.alert('Registrasi Gagal', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Daftar Akun</Text>

        <TouchableOpacity style={styles.photoButton} onPress={pickImage}>
          {formData.profile_photo ? (
            <Image
              source={{ uri: `data:image/jpeg;base64,${formData.profile_photo}` }}
              style={styles.photo}
            />
          ) : (
            <View style={styles.photoPlaceholder}>
              <Ionicons name="camera" size={40} color="#FF6B9D" />
              <Text style={styles.photoText}>Tambah Foto</Text>
            </View>
          )}
        </TouchableOpacity>

        <View style={styles.inputContainer}>
          <Ionicons name="person-outline" size={24} color="#FF6B9D" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Nama Lengkap"
            value={formData.name}
            onChangeText={(text) => setFormData({ ...formData, name: text })}
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.inputContainer}>
          <Ionicons name="at" size={24} color="#FF6B9D" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Username"
            value={formData.username}
            onChangeText={(text) => setFormData({ ...formData, username: text })}
            autoCapitalize="none"
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.inputContainer}>
          <Ionicons name="mail-outline" size={24} color="#FF6B9D" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Email"
            value={formData.email}
            onChangeText={(text) => setFormData({ ...formData, email: text })}
            keyboardType="email-address"
            autoCapitalize="none"
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.inputContainer}>
          <Ionicons name="calendar-outline" size={24} color="#FF6B9D" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Tanggal Lahir (YYYY-MM-DD)"
            value={formData.date_of_birth}
            onChangeText={(text) => setFormData({ ...formData, date_of_birth: text })}
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.genderContainer}>
          <Text style={styles.genderLabel}>Jenis Kelamin:</Text>
          <View style={styles.genderButtons}>
            <TouchableOpacity
              style={[styles.genderButton, formData.gender === 'male' && styles.genderButtonActive]}
              onPress={() => setFormData({ ...formData, gender: 'male' })}
            >
              <Text style={[styles.genderButtonText, formData.gender === 'male' && styles.genderButtonTextActive]}>
                Pria
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.genderButton, formData.gender === 'female' && styles.genderButtonActive]}
              onPress={() => setFormData({ ...formData, gender: 'female' })}
            >
              <Text style={[styles.genderButtonText, formData.gender === 'female' && styles.genderButtonTextActive]}>
                Wanita
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.inputContainer}>
          <Ionicons name="lock-closed-outline" size={24} color="#FF6B9D" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Password"
            value={formData.password}
            onChangeText={(text) => setFormData({ ...formData, password: text })}
            secureTextEntry
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.inputContainer}>
          <Ionicons name="lock-closed-outline" size={24} color="#FF6B9D" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Konfirmasi Password"
            value={formData.confirmPassword}
            onChangeText={(text) => setFormData({ ...formData, confirmPassword: text })}
            secureTextEntry
            placeholderTextColor="#999"
          />
        </View>

        <TouchableOpacity style={styles.locationButton} onPress={getLocation}>
          <Ionicons name="location" size={24} color="#FFF" />
          <Text style={styles.locationButtonText}>
            {formData.latitude !== 0 ? 'Lokasi Aktif' : 'Aktifkan Lokasi'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.button}
          onPress={handleRegister}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <Text style={styles.buttonText}>Daftar</Text>
          )}
        </TouchableOpacity>

        <View style={styles.loginContainer}>
          <Text style={styles.loginText}>Sudah punya akun? </Text>
          <TouchableOpacity onPress={() => router.back()}>
            <Text style={styles.loginLink}>Masuk</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF0F5',
  },
  scrollContent: {
    padding: 24,
    paddingTop: 60,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FF6B9D',
    marginBottom: 24,
    textAlign: 'center',
  },
  photoButton: {
    alignSelf: 'center',
    marginBottom: 24,
  },
  photo: {
    width: 120,
    height: 120,
    borderRadius: 60,
  },
  photoPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FF6B9D',
    borderStyle: 'dashed',
  },
  photoText: {
    marginTop: 8,
    color: '#FF6B9D',
    fontSize: 12,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 16,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    height: 56,
    fontSize: 16,
    color: '#333',
  },
  genderContainer: {
    marginBottom: 16,
  },
  genderLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  genderButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  genderButton: {
    flex: 1,
    height: 48,
    borderRadius: 12,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FF6B9D',
  },
  genderButtonActive: {
    backgroundColor: '#FF6B9D',
  },
  genderButtonText: {
    fontSize: 16,
    color: '#FF6B9D',
    fontWeight: '600',
  },
  genderButtonTextActive: {
    color: '#FFF',
  },
  locationButton: {
    flexDirection: 'row',
    backgroundColor: '#4CAF50',
    borderRadius: 12,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    gap: 8,
  },
  locationButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  button: {
    backgroundColor: '#FF6B9D',
    borderRadius: 12,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 24,
  },
  loginText: {
    fontSize: 16,
    color: '#666',
  },
  loginLink: {
    fontSize: 16,
    color: '#FF6B9D',
    fontWeight: 'bold',
  },
});