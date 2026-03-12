import { FlatList, Text, View } from 'react-native';
import { useGetCategoriesQuery } from '@/store/categoriesApi';

export default function HomeScreen() {
  const { data: categories = [], isLoading, isError, refetch } = useGetCategoriesQuery();

  return (
    <View className="flex-1 bg-black px-6 pt-16">
      <View className="rounded-2xl bg-zinc-900 p-6 border border-zinc-800">
        <Text className="text-2xl text-white font-bold">Категорії</Text>
        <Text className="mt-2 text-zinc-300">
          Дані завантажуються через RTK Query
        </Text>

        {isLoading ? <Text className="text-white mt-4">Завантаження...</Text> : null}

        {isError ? (
          <Text className="text-red-400 mt-4" onPress={() => refetch()}>
            Помилка завантаження. Натисніть, щоб повторити.
          </Text>
        ) : null}

        {!isLoading && !isError ? (
          <FlatList
            data={categories}
            keyExtractor={(item) => String(item.id)}
            className="mt-4"
            ItemSeparatorComponent={() => <View className="h-2" />}
            renderItem={({ item }) => (
              <View className="rounded-xl bg-zinc-800 px-4 py-3">
                <Text className="text-white font-semibold">{item.name}</Text>
              </View>
            )}
            ListEmptyComponent={<Text className="text-zinc-400">Категорій немає</Text>}
          />
        ) : null}
      </View>
    </View>
  );
}
