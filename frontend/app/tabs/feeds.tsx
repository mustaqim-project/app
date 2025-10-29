import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  TextInput,
  Alert,
  ActivityIndicator,
  Modal,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { feedAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import * as ImagePicker from 'expo-image-picker';

export default function FeedsScreen() {
  const [feeds, setFeeds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [content, setContent] = useState('');
  const [images, setImages] = useState<string[]>([]);
  const [posting, setPosting] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    loadFeeds();
  }, []);

  const loadFeeds = async () => {
    setLoading(true);
    try {
      const response = await feedAPI.getFeeds(1);
      setFeeds(response.data.feeds);
    } catch (error) {
      console.error('Load feeds error:', error);
    } finally {
      setLoading(false);
    }
  };

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Required', 'Mohon izinkan akses ke galeri foto');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.5,
      base64: true,
    });

    if (!result.canceled && result.assets[0].base64) {
      setImages([...images, result.assets[0].base64]);
    }
  };

  const handlePost = async () => {
    if (!content && images.length === 0) {
      Alert.alert('Error', 'Silakan tulis sesuatu atau tambahkan gambar');
      return;
    }

    setPosting(true);
    try {
      await feedAPI.createFeed(content, images);
      Alert.alert('Sukses', 'Feed berhasil diposting!');
      setModalVisible(false);
      setContent('');
      setImages([]);
      loadFeeds();
    } catch (error) {
      Alert.alert('Error', 'Gagal memposting feed');
    } finally {
      setPosting(false);
    }
  };

  const renderFeed = ({ item }: { item: any }) => (
    <View style={styles.feedItem}>
      <View style={styles.feedHeader}>
        {item.user.profile_photo ? (
          <Image
            source={{ uri: `data:image/jpeg;base64,${item.user.profile_photo}` }}
            style={styles.avatar}
          />
        ) : (
          <View style={styles.avatarPlaceholder}>
            <Ionicons name="person" size={24} color="#999" />
          </View>
        )}
        <View style={styles.feedUserInfo}>
          <Text style={styles.feedUserName}>{item.user.name}</Text>
          <Text style={styles.feedTime}>{new Date(item.created_at).toLocaleDateString('id-ID')}</Text>
        </View>
      </View>

      <Text style={styles.feedContent}>{item.content}</Text>

      {item.images && item.images.length > 0 && (
        <Image
          source={{ uri: `data:image/jpeg;base64,${item.images[0]}` }}
          style={styles.feedImage}
        />
      )}
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B9D" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Feeds</Text>
        <TouchableOpacity onPress={() => setModalVisible(true)}>
          <Ionicons name="add-circle" size={32} color="#FF6B9D" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={feeds}
        renderItem={renderFeed}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="newspaper-outline" size={80} color="#CCC" />
            <Text style={styles.emptyText}>Belum ada feeds</Text>
          </View>
        }
      />

      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.modalContainer}
        >
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={28} color="#333" />
              </TouchableOpacity>
              <Text style={styles.modalTitle}>Buat Feed</Text>
              <TouchableOpacity
                onPress={handlePost}
                disabled={posting}
              >
                {posting ? (
                  <ActivityIndicator color="#FF6B9D" />
                ) : (
                  <Text style={styles.postButton}>Post</Text>
                )}
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.textInput}
              placeholder="Apa yang Anda pikirkan?"
              value={content}
              onChangeText={setContent}
              multiline
              placeholderTextColor="#999"
            />

            {images.length > 0 && (
              <View style={styles.imagePreview}>
                {images.map((img, index) => (
                  <Image
                    key={index}
                    source={{ uri: `data:image/jpeg;base64,${img}` }}
                    style={styles.previewImage}
                  />
                ))}
              </View>
            )}

            <TouchableOpacity style={styles.addImageButton} onPress={pickImage}>
              <Ionicons name="image" size={24} color="#FF6B9D" />
              <Text style={styles.addImageText}>Tambah Gambar</Text>
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
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
  list: {
    padding: 16,
  },
  feedItem: {
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
  feedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    marginRight: 12,
  },
  avatarPlaceholder: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F0F0F0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  feedUserInfo: {
    flex: 1,
  },
  feedUserName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  feedTime: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  feedContent: {
    fontSize: 14,
    color: '#333',
    marginBottom: 12,
    lineHeight: 20,
  },
  feedImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginTop: 16,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  modalContent: {
    backgroundColor: '#FFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    minHeight: 400,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  postButton: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FF6B9D',
  },
  textInput: {
    fontSize: 16,
    color: '#333',
    minHeight: 120,
    textAlignVertical: 'top',
    marginBottom: 16,
  },
  imagePreview: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16,
  },
  previewImage: {
    width: 100,
    height: 100,
    borderRadius: 8,
  },
  addImageButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#FF6B9D',
    borderStyle: 'dashed',
    gap: 8,
  },
  addImageText: {
    fontSize: 16,
    color: '#FF6B9D',
    fontWeight: '600',
  },
});