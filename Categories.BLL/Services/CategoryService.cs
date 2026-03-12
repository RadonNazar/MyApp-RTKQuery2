using Categories.BLL.Models;
using Categories.DAL.Models;
using Categories.DAL.Repositories;

namespace Categories.BLL.Services;

public class CategoryService
{
    private readonly CategoryRepository _repository = new();

    public List<CategoryDto> GetCategories(string baseUrl)
    {
        return _repository
            .GetCategories()
            .Select(category => MapCategory(category, baseUrl))
            .ToList();
    }

    public CategoryDto CreateCategory(CreateCategoryDto category, string baseUrl)
    {
        var createdCategory = _repository.AddCategory(
            category.Name.Trim(),
            category.ImageUrl.Trim());

        return MapCategory(createdCategory, baseUrl);
    }

    private static CategoryDto MapCategory(Category category, string baseUrl)
    {
        return new CategoryDto
        {
            Id = category.Id,
            Name = category.Name,
            ImageUrl = BuildImageUrl(category.ImageUrl, baseUrl),
        };
    }

    private static string BuildImageUrl(string imageUrl, string baseUrl)
    {
        if (Uri.TryCreate(imageUrl, UriKind.Absolute, out _))
        {
            return imageUrl;
        }

        if (imageUrl.StartsWith('/'))
        {
            return $"{baseUrl}{imageUrl}";
        }

        return $"{baseUrl}/{imageUrl.TrimStart('/')}";
    }
}
