using Godot;

public partial class Sign : Sprite2D
{
	[Export]
	public Texture2D SoundTexture;
	[Export]
	public Texture2D VocalTexture;
	[Export]
	public Texture2D KeyboardTexture;

	public override void _Ready()
	{
		base._Ready();
		switch(GameMaster.Instance.Mode){
			case 0:
				Texture = KeyboardTexture;
				break;
			case 1:
				Texture = VocalTexture;
				break;
			case 2:
				Texture = SoundTexture;
				break;
			default:
				Texture = null;
				break;
		}
	}
}
