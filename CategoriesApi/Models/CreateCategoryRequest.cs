using System.ComponentModel.DataAnnotations;

namespace CategoriesApi.Models;

public class CreateCategoryRequest
{
    [Required(ErrorMessage = "Name is required.")]
    [StringLength(40, MinimumLength = 2, ErrorMessage = "Name must be between 2 and 40 characters.")]
    public string Name { get; set; } = "";

    [Required(ErrorMessage = "ImageUrl is required.")]
    [StringLength(200, ErrorMessage = "ImageUrl must be shorter than 200 characters.")]
    [RegularExpression(@"^(https?:\/\/.+|\/.+)$", ErrorMessage = "ImageUrl must be an absolute URL or start with /.")]
    public string ImageUrl { get; set; } = "";
}
