using Godot;
using System;

public partial class ControlText : Label
{
	[Export(PropertyHint.MultilineText)]
	public string KeyboardText;
	[Export(PropertyHint.MultilineText)]
	public string VocalText;
	[Export(PropertyHint.MultilineText)]
	public string SoundText;
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		switch(GameMaster.Instance.Mode)
		{
			case 0:
				Text = KeyboardText;
				break;
			case 1:
				Text = VocalText;
				break;
			case 2:
				Text = SoundText;
				break;
			default:
				break;
		}
	}
}
