using Godot;

public partial class Book : Node2D, IInteractable
{
    [Export]
    public string TranslatedKeyboard = "";
    [Export]
    public string UntranslatedKeyboard = "";
	[Export]
	public string TranslatedAudio = "";
    [Export]
    public string UntranslatedAudio = "";

    [Export]
    private BookMenu _bookMenu;

	public string Translated
	{
		get
		{
            return GameMaster.Instance.AudioMode ? TranslatedAudio : TranslatedKeyboard;
        }
	}

	public string Untranslated
	{
		get
		{
			return GameMaster.Instance.AudioMode ? UntranslatedAudio : UntranslatedKeyboard;
		}
	}

	public override void _Ready()
	{
        base._Ready();
		if (_bookMenu is null)
		{
            GD.PushError("Book " + Name + " requires _bookMenu to be set");
        }
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
