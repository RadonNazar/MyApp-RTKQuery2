import { useState } from 'react';
import { KeyboardAvoidingView, Platform, ScrollView, Text, View } from 'react-native';

import { CustomButton } from '@/components/ui/custom-button';
import { CustomInput } from '@/components/ui/custom-input';
import { useCreateCategoryMutation } from '@/store/categoriesApi';

type FormValues = {
  name: string;
  imageUrl: string;
};

type FormErrors = Partial<Record<keyof FormValues, string>>;

const initialValues: FormValues = {
  name: '',
  imageUrl: '',
};

function validateName(name: string) {
  const value = name.trim();

  if (!value) {
    return 'Введіть назву категорії.';
  }

  if (value.length < 2) {
    return 'Назва має містити щонайменше 2 символи.';
  }

  if (value.length > 40) {
    return 'Назва має містити не більше 40 символів.';
  }

  return '';
}

function validateImageUrl(imageUrl: string) {
  const value = imageUrl.trim();

  if (!value) {
    return 'Додайте посилання на зображення.';
  }

  const isAbsoluteUrl = /^https?:\/\/.+/i.test(value);
  const isServerPath = /^\/.+/.test(value);

  if (!isAbsoluteUrl && !isServerPath) {
    return 'Використайте повний URL або шлях, що починається з /.';
  }

  return '';
}

function validateForm(values: FormValues): FormErrors {
  const errors: FormErrors = {};

  const nameError = validateName(values.name);
  const imageUrlError = validateImageUrl(values.imageUrl);

  if (nameError) {
    errors.name = nameError;
  }

  if (imageUrlError) {
    errors.imageUrl = imageUrlError;
  }

  return errors;
}

function getApiErrorMessage(error: unknown) {
  if (!error || typeof error !== 'object' || !('data' in error)) {
    return 'Не вдалося створити категорію. Спробуйте ще раз.';
  }

  const data = error.data;

  if (data && typeof data === 'object' && 'errors' in data) {
    const modelState = data.errors;

    if (modelState && typeof modelState === 'object') {
      const firstError = Object.values(modelState)
        .flat()
        .find((message): message is string => typeof message === 'string');

      if (firstError) {
        return firstError;
      }
    }
  }

  if (data && typeof data === 'object' && 'title' in data && typeof data.title === 'string') {
    return data.title;
  }

  return 'Не вдалося створити категорію. Спробуйте ще раз.';
}

export default function CreateCategoryScreen() {
  const [values, setValues] = useState<FormValues>(initialValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitError, setSubmitError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [createCategory, { isLoading }] = useCreateCategoryMutation();

  const handleChange = (field: keyof FormValues) => (value: string) => {
    setValues((current) => ({
      ...current,
      [field]: value,
    }));

    setErrors((current) => ({
      ...current,
      [field]: undefined,
    }));
    setSubmitError('');
    setSuccessMessage('');
  };

  const handleBlur = (field: keyof FormValues) => () => {
    const validationMessage =
      field === 'name' ? validateName(values.name) : validateImageUrl(values.imageUrl);

    setErrors((current) => ({
      ...current,
      [field]: validationMessage || undefined,
    }));
  };

  const handleSubmit = async () => {
    const nextErrors = validateForm(values);

    setErrors(nextErrors);
    setSubmitError('');
    setSuccessMessage('');

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    try {
      const createdCategory = await createCategory({
        name: values.name.trim(),
        imageUrl: values.imageUrl.trim(),
      }).unwrap();

      setValues(initialValues);
      setErrors({});
      setSuccessMessage(
        `Категорію "${createdCategory.name}" створено. Вона з'явиться на вкладці Home.`
      );
    } catch (error) {
      setSubmitError(getApiErrorMessage(error));
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      className="flex-1 bg-black">
      <ScrollView
        className="flex-1"
        contentContainerStyle={{ paddingHorizontal: 24, paddingTop: 64, paddingBottom: 32 }}
        keyboardShouldPersistTaps="handled">
        <View className="rounded-[28px] border border-zinc-800 bg-zinc-900 p-6">
          <Text className="text-3xl font-bold text-white">Створити категорію</Text>
          <Text className="mt-3 text-base leading-6 text-zinc-300">
            Форма використовує кастомні інпути, власну кнопку та ручну валідацію перед RTK Query
            mutation.
          </Text>

          <View className="mt-8">
            <CustomInput
              label="Назва"
              placeholder="Наприклад, Kids"
              value={values.name}
              onChangeText={handleChange('name')}
              onBlur={handleBlur('name')}
              error={errors.name}
              hint="2-40 символів. Назва має бути зрозумілою для списку категорій."
              autoCapitalize="words"
              returnKeyType="next"
            />

            <CustomInput
              label="Зображення"
              placeholder="https://example.com/image.jpg або /images/kids.jpg"
              value={values.imageUrl}
              onChangeText={handleChange('imageUrl')}
              onBlur={handleBlur('imageUrl')}
              error={errors.imageUrl}
              hint="Можна передати зовнішній URL або шлях до зображення на сервері."
              autoCapitalize="none"
              keyboardType="url"
              autoCorrect={false}
            />
          </View>

          {submitError ? <Text className="mb-4 text-sm text-rose-400">{submitError}</Text> : null}
          {successMessage ? (
            <Text className="mb-4 text-sm text-emerald-400">{successMessage}</Text>
          ) : null}

          <CustomButton
            title={isLoading ? 'Створення...' : 'Створити категорію'}
            onPress={handleSubmit}
            loading={isLoading}
          />

          <View className="mt-6 rounded-2xl border border-zinc-800 bg-black/40 p-4">
            <Text className="text-sm font-semibold uppercase tracking-[1px] text-zinc-500">
              Як це працює
            </Text>
            <Text className="mt-3 text-sm leading-6 text-zinc-300">
              Після успішного submit RTK Query invalidates список категорій, тому на вкладці Home
              ви бачите вже оновлені дані.
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
