using Godot;

public partial class BookMenu : Control
{
	// Instructions based on audio/keyboard mode and (un)translated mode
    [Export]
    public string UntranslatedAudioInstructions = "\n\nSæ \"brœs\" tra clænx thës ovra'lei";
    [Export]
    public string UntranslatedKeyboardInstructions = "\n\nPrš \"ɘ\" tra chœ̆l thîs uvea'lea";
    [Export]
    public string TranslatedAudioInstructions = "\n\nSay \"close\" to close this overlay";
    [Export]
    public string TranslatedKeyboardInstructions = "\n\nPress \"e\" to close this overlay";

	// Helper variables for getting the (un)translated versions based on the audio mode
	public string UntranslatedInstructions {
		get {
            return GameMaster.Instance.AudioMode ? UntranslatedAudioInstructions : UntranslatedKeyboardInstructions;
        }
	}

	public string TranslatedInstructions {
		get {
            return GameMaster.Instance.AudioMode ? TranslatedAudioInstructions : TranslatedKeyboardInstructions;
        }
	}

    private Label _label;
    private Book _activeBook;

    public override void _Ready()
	{
        base._Ready();
        _label = GetNode<Label>("ColorRect/Label");
    }

    public override void _Process(double delta)
    {
        base._Process(delta);
		// Handles user input for translating book
		if (Input.IsActionPressed("Translate"))
		{
            Translate();
        }
    }

	public void Translate()
	{
        _label.Text = _activeBook.Translated + TranslatedInstructions;
    }

	public bool IsOpen(Book book)
	{
        return IsInstanceValid(_activeBook) && _activeBook == book;
    }

    public void Open(Book book)
	{
        _activeBook = book;
        Visible = true;
        _label.Text = _activeBook.Untranslated + UntranslatedInstructions;
    }

	public void Close()
	{
		_activeBook = null;
        Visible = false;
        _label.Text = "This is some test text.";
    }
}
