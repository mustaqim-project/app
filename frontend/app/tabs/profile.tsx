import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { profileAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

export default function ProfileScreen() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { logout, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const response = await profileAPI.getMyProfile();
      setProfile(response.data);
    } catch (error) {
      console.error('Load profile error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Apakah Anda yakin ingin keluar?',
      [
        { text: 'Batal', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/auth/login');
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B9D" />
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Gagal memuat profil</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Profil</Text>
        <TouchableOpacity onPress={handleLogout}>
          <Ionicons name="log-out-outline" size={28} color="#FF6B6B" />
        </TouchableOpacity>
      </View>

      <View style={styles.profileSection}>
        <View style={styles.photoContainer}>
          {profile.profile_photos && profile.profile_photos.length > 0 ? (
            <Image
              source={{ uri: `data:image/jpeg;base64,${profile.profile_photos[0]}` }}
              style={styles.profilePhoto}
            />
          ) : (
            <View style={styles.profilePhotoPlaceholder}>
              <Ionicons name="person" size={80} color="#999" />
            </View>
          )}
          {profile.verified_face && (
            <View style={styles.verifiedBadge}>
              <Ionicons name="checkmark-circle" size={32} color="#4CAF50" />
            </View>
          )}
        </View>

        <Text style={styles.profileName}>{profile.name}, {profile.age}</Text>
        <Text style={styles.profileUsername}>@{profile.username}</Text>
        {profile.bio && <Text style={styles.profileBio}>{profile.bio}</Text>}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Hasil Asesmen</Text>

        <View style={styles.assessmentCard}>
          <View style={styles.assessmentItem}>
            <Ionicons name="person-outline" size={24} color="#FF6B9D" />
            <View style={styles.assessmentInfo}>
              <Text style={styles.assessmentLabel}>MBTI</Text>
              <Text style={styles.assessmentValue}>{profile.mbti || 'Belum diisi'}</Text>
            </View>
          </View>

          <View style={styles.assessmentItem}>
            <Ionicons name="heart-outline" size={24} color="#FF6B9D" />
            <View style={styles.assessmentInfo}>
              <Text style={styles.assessmentLabel}>Love Language</Text>
              <Text style={styles.assessmentValue}>{profile.love_language || 'Belum diisi'}</Text>
            </View>
          </View>

          <View style={styles.assessmentItem}>
            <Ionicons name="checkmark-circle-outline" size={24} color="#FF6B9D" />
            <View style={styles.assessmentInfo}>
              <Text style={styles.assessmentLabel}>Kesiapan Hubungan</Text>
              <Text style={[styles.assessmentValue, profile.readiness >= 80 ? styles.readyScore : styles.notReadyScore]}>
                {profile.readiness ? `${profile.readiness.toFixed(0)}%` : '0%'}
              </Text>
            </View>
          </View>

          <View style={styles.assessmentItem}>
            <Ionicons name="sunny-outline" size={24} color="#FF6B9D" />
            <View style={styles.assessmentInfo}>
              <Text style={styles.assessmentLabel}>Temperamen</Text>
              <Text style={styles.assessmentValue}>{profile.temperament || 'Belum diisi'}</Text>
            </View>
          </View>

          <View style={styles.assessmentItem}>
            <Ionicons name="analytics-outline" size={24} color="#FF6B9D" />
            <View style={styles.assessmentInfo}>
              <Text style={styles.assessmentLabel}>DISC</Text>
              <Text style={styles.assessmentValue}>{profile.disc || 'Belum diisi'}</Text>
            </View>
          </View>
        </View>
      </View>

      {profile.readiness < 80 && (
        <View style={styles.warningCard}>
          <Ionicons name="warning" size={24} color="#FF6B6B" />
          <Text style={styles.warningText}>
            Skor kesiapan Anda di bawah 80%. Beberapa fitur seperti konsultasi tidak tersedia.
          </Text>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Pengaturan</Text>
        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="settings-outline" size={24} color="#666" />
          <Text style={styles.menuText}>Pengaturan Akun</Text>
          <Ionicons name="chevron-forward" size={24} color="#CCC" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="lock-closed-outline" size={24} color="#666" />
          <Text style={styles.menuText}>Privasi</Text>
          <Ionicons name="chevron-forward" size={24} color="#CCC" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="help-circle-outline" size={24} color="#666" />
          <Text style={styles.menuText}>Bantuan</Text>
          <Ionicons name="chevron-forward" size={24} color="#CCC" />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF0F5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFF0F5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingTop: 60,
    backgroundColor: '#FFF',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF6B9D',
  },
  profileSection: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#FFF',
    marginBottom: 16,
  },
  photoContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  profilePhoto: {
    width: 120,
    height: 120,
    borderRadius: 60,
  },
  profilePhotoPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#F0F0F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  verifiedBadge: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    backgroundColor: '#FFF',
    borderRadius: 16,
  },
  profileName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  profileUsername: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  profileBio: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  section: {
    backgroundColor: '#FFF',
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  assessmentCard: {
    gap: 12,
  },
  assessmentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#FFF0F5',
    borderRadius: 8,
  },
  assessmentInfo: {
    flex: 1,
    marginLeft: 12,
  },
  assessmentLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 2,
  },
  assessmentValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  readyScore: {
    color: '#4CAF50',
  },
  notReadyScore: {
    color: '#FF6B6B',
  },
  warningCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#FF6B6B',
    gap: 12,
  },
  warningText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  menuText: {
    flex: 1,
    fontSize: 16,
    color: '#333',
    marginLeft: 12,
  },
});