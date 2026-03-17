import { Modal, Text, View } from 'react-native';
import { CustomButton } from './custom-button';

type Props = {
  visible: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
};

export function ConfirmModal({
  visible,
  onConfirm,
  onCancel,
  loading,
}: Props) {
  return (
    <Modal transparent visible={visible} animationType="fade">
      <View className="flex-1 bg-black/70 justify-center items-center px-6">
        <View className="bg-zinc-900 w-full rounded-2xl p-6">
          <Text className="text-white text-lg font-bold mb-4">
            Ви впевнені?
          </Text>

          <Text className="text-gray-400 mb-6">
            Цю дію неможливо скасувати
          </Text>

          <View className="flex-row gap-3">
            <View className="flex-1">
              <CustomButton
                title="Скасувати"
                onPress={onCancel}
                disabled={loading}
              />
            </View>

            <View className="flex-1">
              <CustomButton
                title="Так, видалити"
                onPress={onConfirm}
                loading={loading}
              />
            </View>
          </View>
        </View>
      </View>
    </Modal>
  );
}