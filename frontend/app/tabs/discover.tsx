import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { discoveryAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const { width, height } = Dimensions.get('window');

export default function DiscoverScreen() {
  const [users, setUsers] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [radius, setRadius] = useState(50);
  const { user } = useAuth();

  useEffect(() => {
    loadUsers();
  }, [radius]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await discoveryAPI.getUsers(radius, 1);
      setUsers(response.data.users);
      setCurrentIndex(0);
    } catch (error: any) {
      if (error.response?.status === 403) {
        Alert.alert('Perhatian', 'Selesaikan asesmen terlebih dahulu');
      } else {
        Alert.alert('Error', 'Gagal memuat pengguna');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (currentIndex >= users.length) return;

    const currentUser = users[currentIndex];
    try {
      const response = await discoveryAPI.likeUser(currentUser.id);
      
      if (response.data.match) {
        Alert.alert(
          '🎉 It\'s a Match!',
          `Anda dan ${currentUser.name} saling menyukai!`,
          [
            { text: 'OK', onPress: () => nextUser() }
          ]
        );
      } else {
        nextUser();
      }
    } catch (error) {
      Alert.alert('Error', 'Gagal mengirim like');
    }
  };

  const handlePass = () => {
    nextUser();
  };

  const nextUser = () => {
    if (currentIndex < users.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      Alert.alert('Habis', 'Tidak ada pengguna lagi. Coba perluas radius pencarian.');
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B9D" />
      </View>
    );
  }

  if (users.length === 0 || currentIndex >= users.length) {
    return (
      <View style={styles.emptyContainer}>
        <Ionicons name="search" size={80} color="#CCC" />
        <Text style={styles.emptyText}>Tidak ada pengguna ditemukan</Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={loadUsers}
        >
          <Text style={styles.refreshButtonText}>Muat Ulang</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const currentUser = users[currentIndex];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Discover</Text>
        <TouchableOpacity onPress={() => Alert.alert('Radius', `Radius saat ini: ${radius} km`)}>
          <Ionicons name="options" size={24} color="#FF6B9D" />
        </TouchableOpacity>
      </View>

      <View style={styles.cardContainer}>
        <Image
          source={{ uri: `data:image/jpeg;base64,${currentUser.profile_photos[0]}` }}
          style={styles.cardImage}
        />
        <View style={styles.cardInfo}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardName}>
              {currentUser.name}, {currentUser.age}
            </Text>
            {currentUser.verified_face && (
              <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
            )}
          </View>
          <Text style={styles.cardDetail}>
            <Ionicons name="location" size={16} /> {currentUser.distance} km
          </Text>
          <Text style={styles.cardDetail}>
            <Ionicons name="heart" size={16} /> Compatibility: {currentUser.compatibility}%
          </Text>
          {currentUser.mbti && (
            <Text style={styles.cardDetail}>MBTI: {currentUser.mbti}</Text>
          )}
          {currentUser.love_language && (
            <Text style={styles.cardDetail}>Love Language: {currentUser.love_language}</Text>
          )}
        </View>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.actionButton, styles.passButton]}
          onPress={handlePass}
        >
          <Ionicons name="close" size={32} color="#FFF" />
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.actionButton, styles.likeButton]}
          onPress={handleLike}
        >
          <Ionicons name="heart" size={32} color="#FFF" />
        </TouchableOpacity>
      </View>
    </View>
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFF0F5',
    padding: 24,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginTop: 16,
    marginBottom: 24,
  },
  refreshButton: {
    backgroundColor: '#FF6B9D',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },
  refreshButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
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
  cardContainer: {
    flex: 1,
    margin: 16,
    borderRadius: 16,
    backgroundColor: '#FFF',
    overflow: 'hidden',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
  },
  cardImage: {
    width: '100%',
    height: '70%',
  },
  cardInfo: {
    padding: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 8,
  },
  cardDetail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingBottom: 32,
    gap: 32,
  },
  actionButton: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  passButton: {
    backgroundColor: '#FF6B6B',
  },
  likeButton: {
    backgroundColor: '#FF6B9D',
  },
});