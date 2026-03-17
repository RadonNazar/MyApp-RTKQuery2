import { useState } from 'react';
import { FlatList, Text, View, Pressable } from 'react-native';

import {
  useGetCategoriesQuery,
  useDeleteCategoryMutation,
} from '@/store/categoriesApi';

import { ConfirmModal } from '@/components/ui/confirm-modal';

export default function HomeScreen() {
  const { data: categories = [], isLoading } = useGetCategoriesQuery();
  const [deleteCategory, { isLoading: isDeleting }] =
    useDeleteCategoryMutation();

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  function openModal(id: number) {
    setSelectedId(id);
    setModalVisible(true);
  }

  function closeModal() {
    setModalVisible(false);
    setSelectedId(null);
  }

  async function handleDelete() {
    if (!selectedId) return;

    try {
      await deleteCategory(selectedId).unwrap();
      closeModal();
    } catch (e) {
      console.log(e);
    }
  }

  if (isLoading) {
    return (
      <View className="flex-1 justify-center items-center bg-black">
        <Text className="text-white">Loading...</Text>
      </View>
    );
  }

  return (
    <View className="flex-1 bg-black p-4">
      <FlatList
        data={categories}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <View className="flex-row justify-between items-center mb-4">
            <Text className="text-white text-lg">{item.name}</Text>

            <Pressable onPress={() => openModal(item.id)}>
              <Text className="text-red-500">Видалити</Text>
            </Pressable>
          </View>
        )}
      />

      <ConfirmModal
        visible={modalVisible}
        onCancel={closeModal}
        onConfirm={handleDelete}
        loading={isDeleting}
      />
    </View>
  );
}