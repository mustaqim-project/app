import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Modal,
  TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { consultationAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

export default function ConsultationScreen() {
  const [counselors, setCounselors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedCounselor, setSelectedCounselor] = useState<any>(null);
  const [schedule, setSchedule] = useState('');
  const [sessionType, setSessionType] = useState('chat');
  const [booking, setBooking] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    loadCounselors();
  }, []);

  const loadCounselors = async () => {
    setLoading(true);
    try {
      const response = await consultationAPI.getCounselors();
      setCounselors(response.data.counselors);
    } catch (error: any) {
      if (error.response?.status === 403) {
        Alert.alert(
          'Akses Ditolak',
          'Fitur konsultasi hanya tersedia untuk pengguna dengan skor kesiapan 80% atau lebih. Skor Anda saat ini: ' + (user?.readiness || 0) + '%',
          [{ text: 'OK' }]
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleBook = async () => {
    if (!schedule) {
      Alert.alert('Error', 'Silakan pilih jadwal');
      return;
    }

    setBooking(true);
    try {
      const response = await consultationAPI.bookConsultation({
        counselor_id: selectedCounselor.id,
        schedule,
        session_type: sessionType,
      });

      Alert.alert(
        'Booking Berhasil!',
        'Konsultasi Anda telah dikonfirmasi. ID Pembayaran: ' + response.data.payment_id,
        [
          {
            text: 'OK',
            onPress: () => {
              setModalVisible(false);
              setSchedule('');
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Gagal melakukan booking');
    } finally {
      setBooking(false);
    }
  };

  const renderCounselor = ({ item }: { item: any }) => (
    <TouchableOpacity
      style={styles.counselorCard}
      onPress={() => {
        setSelectedCounselor(item);
        setModalVisible(true);
      }}
    >
      <View style={styles.counselorIcon}>
        <Ionicons name="person" size={40} color="#FF6B9D" />
      </View>
      <View style={styles.counselorInfo}>
        <Text style={styles.counselorName}>{item.name}</Text>
        <Text style={styles.counselorSpec}>{item.specialization}</Text>
        <View style={styles.counselorMeta}>
          <View style={styles.rating}>
            <Ionicons name="star" size={16} color="#FFC107" />
            <Text style={styles.ratingText}>{item.rating}</Text>
          </View>
          <Text style={styles.price}>Rp {item.price.toLocaleString('id-ID')}</Text>
        </View>
      </View>
      <Ionicons name="chevron-forward" size={24} color="#CCC" />
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF6B9D" />
      </View>
    );
  }

  if (!user || user.readiness < 80) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Konsultasi</Text>
        </View>
        <View style={styles.restrictedContainer}>
          <Ionicons name="lock-closed" size={80} color="#FF6B6B" />
          <Text style={styles.restrictedTitle}>Akses Terbatas</Text>
          <Text style={styles.restrictedText}>
            Fitur konsultasi hanya tersedia untuk pengguna dengan skor kesiapan hubungan 80% atau lebih.
          </Text>
          <Text style={styles.restrictedScore}>
            Skor Anda saat ini: {user?.readiness || 0}%
          </Text>
          <Text style={styles.restrictedHint}>
            Tingkatkan skor Anda dengan mengikuti asesmen ulang.
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Konsultasi</Text>
      </View>

      <FlatList
        data={counselors}
        renderItem={renderCounselor}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="people-outline" size={80} color="#CCC" />
            <Text style={styles.emptyText}>Belum ada konselor tersedia</Text>
          </View>
        }
      />

      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Booking Konsultasi</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={28} color="#333" />
              </TouchableOpacity>
            </View>

            {selectedCounselor && (
              <View>
                <Text style={styles.modalCounselorName}>{selectedCounselor.name}</Text>
                <Text style={styles.modalCounselorSpec}>{selectedCounselor.specialization}</Text>
                <Text style={styles.modalPrice}>
                  Rp {selectedCounselor.price.toLocaleString('id-ID')}
                </Text>

                <Text style={styles.label}>Tipe Sesi:</Text>
                <View style={styles.sessionTypeButtons}>
                  <TouchableOpacity
                    style={[
                      styles.sessionTypeButton,
                      sessionType === 'chat' && styles.sessionTypeButtonActive,
                    ]}
                    onPress={() => setSessionType('chat')}
                  >
                    <Text
                      style={[
                        styles.sessionTypeText,
                        sessionType === 'chat' && styles.sessionTypeTextActive,
                      ]}
                    >
                      Chat
                    </Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[
                      styles.sessionTypeButton,
                      sessionType === 'video' && styles.sessionTypeButtonActive,
                    ]}
                    onPress={() => setSessionType('video')}
                  >
                    <Text
                      style={[
                        styles.sessionTypeText,
                        sessionType === 'video' && styles.sessionTypeTextActive,
                      ]}
                    >
                      Video
                    </Text>
                  </TouchableOpacity>
                </View>

                <Text style={styles.label}>Jadwal (YYYY-MM-DD HH:MM):</Text>
                <TextInput
                  style={styles.input}
                  placeholder="2025-01-15 14:00"
                  value={schedule}
                  onChangeText={setSchedule}
                  placeholderTextColor="#999"
                />

                <TouchableOpacity
                  style={styles.bookButton}
                  onPress={handleBook}
                  disabled={booking}
                >
                  {booking ? (
                    <ActivityIndicator color="#FFF" />
                  ) : (
                    <Text style={styles.bookButtonText}>Booking & Bayar (Mock)</Text>
                  )}
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
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
    padding: 16,
    paddingTop: 60,
    backgroundColor: '#FFF',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF6B9D',
  },
  restrictedContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  restrictedTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF6B6B',
    marginTop: 16,
  },
  restrictedText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 24,
  },
  restrictedScore: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FF6B9D',
    marginTop: 16,
  },
  restrictedHint: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
  },
  list: {
    padding: 16,
  },
  counselorCard: {
    flexDirection: 'row',
    alignItems: 'center',
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
  counselorIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#FFF0F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  counselorInfo: {
    flex: 1,
  },
  counselorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  counselorSpec: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  counselorMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  rating: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  ratingText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  price: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#4CAF50',
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
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  modalContent: {
    backgroundColor: '#FFF',
    borderRadius: 24,
    padding: 24,
    width: '90%',
    maxWidth: 400,
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
  modalCounselorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  modalCounselorSpec: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  modalPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 24,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  sessionTypeButtons: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  sessionTypeButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#FF6B9D',
    alignItems: 'center',
  },
  sessionTypeButtonActive: {
    backgroundColor: '#FF6B9D',
  },
  sessionTypeText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF6B9D',
  },
  sessionTypeTextActive: {
    color: '#FFF',
  },
  input: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#333',
    marginBottom: 24,
  },
  bookButton: {
    backgroundColor: '#FF6B9D',
    borderRadius: 12,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  bookButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});