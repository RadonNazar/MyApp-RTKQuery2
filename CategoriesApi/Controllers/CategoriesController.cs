using Microsoft.AspNetCore.Mvc;
using Categories.BLL.Models;
using Categories.BLL.Services;
using CreateCategoryRequest = CategoriesApi.Models.CreateCategoryRequest;

namespace CategoriesApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class CategoriesController : ControllerBase
{
    private readonly CategoryService _service;

    public CategoriesController()
    {
        _service = new CategoryService();
    }

    [HttpGet]
    public ActionResult<List<CategoryDto>> Get()
    {
        var baseUrl = $"{Request.Scheme}://{Request.Host}";

        var categories = _service.GetCategories(baseUrl);

        return Ok(categories);
    }

    [HttpPost]
    public ActionResult<CategoryDto> Create([FromBody] CreateCategoryRequest request)
    {
        var baseUrl = $"{Request.Scheme}://{Request.Host}";

        var category = _service.CreateCategory(
            new CreateCategoryDto
            {
                Name = request.Name,
                ImageUrl = request.ImageUrl,
            },
            baseUrl);

        return Created($"{Request.Path}/{category.Id}", category);
    }
}
