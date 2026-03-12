import { Text, TextInput, TextInputProps, View } from 'react-native';

type CustomInputProps = TextInputProps & {
  label: string;
  hint?: string;
  error?: string;
};

export function CustomInput({ label, hint, error, ...props }: CustomInputProps) {
  const stateClasses = error
    ? 'border-rose-500 bg-rose-950/20'
    : 'border-zinc-700 bg-zinc-950';

  return (
    <View className="mb-5">
      <Text className="mb-2 text-sm font-semibold uppercase tracking-[1px] text-zinc-400">
        {label}
      </Text>
      <TextInput
        {...props}
        placeholderTextColor="#71717A"
        className={`rounded-2xl border px-4 py-4 text-base text-white ${stateClasses}`}
      />
      {error ? <Text className="mt-2 text-sm text-rose-400">{error}</Text> : null}
      {!error && hint ? <Text className="mt-2 text-sm text-zinc-500">{hint}</Text> : null}
    </View>
  );
}
