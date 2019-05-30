using System;
using System.Linq;

[Serializable]
public abstract class EmeraldException : Exception {
    public static int code;

    new string Message;

    protected EmeraldException(string message) : base(message) {
    }

    public static EmeraldException GetException(Error error) {
        // Searches for the derived class with the given code
        var exceptionType = (from domainAssembly in AppDomain.CurrentDomain.GetAssemblies()
                             from assemblyType in domainAssembly.GetTypes()
                             where typeof(EmeraldException).IsAssignableFrom(assemblyType)
                             select assemblyType).First(t => (int) t.GetField("code").GetValue(null) == error.Code);
        var ex = (EmeraldException) Activator.CreateInstance(exceptionType, error.Message);
        ex.Message = error.Message;

        return ex;
    }
}

public class PlayerInvalidLogin : EmeraldException {
    public new static int code = 1;

    public PlayerInvalidLogin(string message) : base(message) {
    }
}

public class PlayerInvalidAuthToken : EmeraldException {
    public new static int code = 2;

    public PlayerInvalidAuthToken(string message) : base(message) {
    }
}

public class MatchCreationError : EmeraldException {
    public new static int code = 3;

    public MatchCreationError(string message) : base(message) {
    }
}

public class InvalidGameKey : EmeraldException {
    public new static int code = 4;

    public InvalidGameKey(string message) : base(message) {
    }
}

public class InvalidMatchType : EmeraldException {
    public new static int code = 5;

    public InvalidMatchType(string message) : base(message) {
    }
}

public class MissingFieldError : EmeraldException {
    public new static int code = 6;

    public MissingFieldError(string message) : base(message) {
    }
}

public class MatchStartMatchError : EmeraldException {
    public new static int code = 7;

    public MatchStartMatchError(string message) : base(message) {
    }
}

public class MatchCreateUserGroupError : EmeraldException {
    public new static int code = 8;

    public MatchCreateUserGroupError(string message) : base(message) {
    }
}

public class GameNotFound : EmeraldException {
    public new static int code = 9;

    public GameNotFound(string message) : base(message) {
    }
}

public class MatchNotFound : EmeraldException {
    public new static int code = 10;

    public MatchNotFound(string message) : base(message) {
    }
}

public class PlayerGroupNotFound : EmeraldException {
    public new static int code = 11;

    public PlayerGroupNotFound(string message) : base(message) {
    }
}

public class PlayerNotFound : EmeraldException {
    public new static int code = 12;

    public PlayerNotFound(string message) : base(message) {
    }
}

public class MatchEndMatchError : EmeraldException {
    public new static int code = 13;

    public MatchEndMatchError(string message) : base(message) {
    }
}

public class MatchAbortMatchError : EmeraldException {
    public new static int code = 14;

    public MatchAbortMatchError(string message) : base(message) {
    }
}

public class PlayerGroupAddPlayerError : EmeraldException {
    public new static int code = 15;

    public PlayerGroupAddPlayerError(string message) : base(message) {
    }
}

public class PlayerQuitError : EmeraldException {
    public new static int code = 16;

    public PlayerQuitError(string message) : base(message) {
    }
}

public class PlayerCreateError : EmeraldException {
    public new static int code = 17;

    public PlayerCreateError(string message) : base(message) {
    }
}

public class GameCreateError : EmeraldException {
    public new static int code = 18;

    public GameCreateError(string message) : base(message) {
    }
}

public class UserAnonymousException : EmeraldException {
    public new static int code = 19;

    public UserAnonymousException(string message) : base(message) {
    }
}

public class UserNotPlayerException : EmeraldException {
    public new static int code = 20;

    public UserNotPlayerException(string message) : base(message) {
    }
}

public class PlayerGroupCreationError : EmeraldException {
    public new static int code = 21;

    public PlayerGroupCreationError(string message) : base(message) {
    }
}

public class MatchTypeCreationError : EmeraldException {
    public new static int code = 22;

    public MatchTypeCreationError(string message) : base(message) {
    }
}

public class MatchTypeGroupCreationError : EmeraldException {
    public new static int code = 23;

    public MatchTypeGroupCreationError(string message) : base(message) {
    }
}

public class RemoveGroupError : EmeraldException {
    public new static int code = 24;

    public RemoveGroupError(string message) : base(message) {
    }
}