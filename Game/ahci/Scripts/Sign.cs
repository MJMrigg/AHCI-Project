using Godot;

public partial class Sign : Sprite2D
{
    [Export]
    public Texture2D AudioTexture;
    [Export]
    public Texture2D KeyboardTexture;

    public override void _Ready()
	{
        base._Ready();
        Texture = GameMaster.Instance.AudioMode ? AudioTexture : KeyboardTexture;
    }
}
