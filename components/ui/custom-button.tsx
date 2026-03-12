import { ActivityIndicator, Pressable, Text } from 'react-native';

type CustomButtonProps = {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  loading?: boolean;
};

export function CustomButton({
  title,
  onPress,
  disabled = false,
  loading = false,
}: CustomButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <Pressable
      onPress={onPress}
      disabled={isDisabled}
      className={`min-h-14 items-center justify-center rounded-2xl px-5 ${
        isDisabled ? 'bg-zinc-800' : 'bg-emerald-400'
      }`}>
      {loading ? (
        <ActivityIndicator color="#09090B" />
      ) : (
        <Text className={`text-base font-bold ${isDisabled ? 'text-zinc-500' : 'text-zinc-950'}`}>
          {title}
        </Text>
      )}
    </Pressable>
  );
}
