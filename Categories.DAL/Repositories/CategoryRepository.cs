using Categories.DAL.Models;

namespace Categories.DAL.Repositories;

public class CategoryRepository
{
    private static readonly List<Category> Categories =
    [
        new() { Id = 1, Name = "Women", ImageUrl = "/images/women.jpg" },
        new() { Id = 2, Name = "Men", ImageUrl = "/images/men.jpg" },
        new() { Id = 3, Name = "Shoes", ImageUrl = "/images/shoes.jpg" },
        new() { Id = 4, Name = "Accessories", ImageUrl = "/images/accessories.jpg" }
    ];

    public List<Category> GetCategories()
    {
        return Categories
            .Select(category => new Category
            {
                Id = category.Id,
                Name = category.Name,
                ImageUrl = category.ImageUrl,
            })
            .ToList();
    }

    public Category AddCategory(string name, string imageUrl)
    {
        var category = new Category
        {
            Id = Categories.Count == 0 ? 1 : Categories.Max(item => item.Id) + 1,
            Name = name,
            ImageUrl = imageUrl,
        };

        Categories.Add(category);

        return new Category
        {
            Id = category.Id,
            Name = category.Name,
            ImageUrl = category.ImageUrl,
        };
    }
}
