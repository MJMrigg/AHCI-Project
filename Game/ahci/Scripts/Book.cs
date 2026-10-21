using Godot;

public partial class Book : Node2D, IInteractable
{
	[Export(PropertyHint.MultilineText)]
	public string TranslatedKeyboard = "";
	[Export(PropertyHint.MultilineText)]
	public string UntranslatedKeyboard = "";
	[Export(PropertyHint.MultilineText)]
	public string TranslatedVocal = "";
	[Export(PropertyHint.MultilineText)]
	public string UntranslatedVocal = "";
	[Export(PropertyHint.MultilineText)]
	public string TranslatedSound = "";
	[Export(PropertyHint.MultilineText)]
	public string UntranslatedSound = "";

	[Export]
	private BookMenu _bookMenu;
	
	[Export]
	private bool _startOpen = true;

	public string Translated
	{
		get
		{
			switch(GameMaster.Instance.Mode)
			{
				case 0:
					return TranslatedKeyboard;
				case 1:
					return TranslatedVocal;
				case 2:
					return TranslatedSound;
				default:
					return "";
			}
		}
	}

	public string Untranslated
	{
		get
		{
			switch(GameMaster.Instance.Mode)
			{
				case 0:
					return UntranslatedKeyboard;
				case 1:
					return UntranslatedVocal;
				case 2:
					return UntranslatedSound;
				default:
					return "";
			}
		}
	}

	public override void _Ready()
	{
		base._Ready();
		if (_bookMenu is null)
		{
			GD.PushError("Book " + Name + " requires _bookMenu to be set");
		}
		else if (_startOpen && !_bookMenu.IsOpen(this))
		{
			this.Interact();
		}
	}

	public override void _Process(double delta)
	{
		base._Process(delta);
	}

	public void Interact()
	{
		if (_bookMenu.IsOpen(this))
		{
			_bookMenu.Close();
		}
		else
		{
			_bookMenu.Open(this);
		}
	}
}
