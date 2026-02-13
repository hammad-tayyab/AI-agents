# ============================================
# EXTREMELY OVERENGINEERED HELLO WORLD PROGRAM
# ============================================

# Step 1: Define a class to hold and manage alphabet data
class AlphabetRepository:

    def __init__(self):
        self._alphabet_storage_container = []
        self._initialize_storage()

    def _initialize_storage(self):
        lowercase_letters = [
            'a','b','c','d','e','f','g','h','i','j','k','l','m',
            'n','o','p','q','r','s','t','u','v','w','x','y','z'
        ]

        uppercase_letters = [
            'A','B','C','D','E','F','G','H','I','J','K','L','M',
            'N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
        ]

        symbols = [' ']

        for letter in lowercase_letters:
            self._alphabet_storage_container.append(letter)

        for letter in uppercase_letters:
            self._alphabet_storage_container.append(letter)

        for symbol in symbols:
            self._alphabet_storage_container.append(symbol)

    def get_storage_reference(self):
        return self._alphabet_storage_container


# Step 2: Define a class responsible for searching characters
class AlphabetSearcher:

    def __init__(self, storage_reference):
        self.storage_reference = storage_reference

    def find_character_by_identity(self, target_character):
        result_character_container = None

        for index_position in range(len(self.storage_reference)):
            current_character_under_inspection = self.storage_reference[index_position]

            if self._compare_characters(
                current_character_under_inspection,
                target_character
            ):
                result_character_container = current_character_under_inspection
                break

        return result_character_container

    def _compare_characters(self, character_one, character_two):
        if character_one == character_two:
            return True
        else:
            return False


# Step 3: Define a builder class for constructing words
class WordConstructionEngine:

    def __init__(self, alphabet_searcher):
        self.alphabet_searcher = alphabet_searcher
        self.internal_character_buffer = []

    def append_character_to_internal_buffer(self, character_to_append):

        found_character = self.alphabet_searcher.find_character_by_identity(
            character_to_append
        )

        if found_character is not None:
            self.internal_character_buffer.append(found_character)

    def retrieve_constructed_word(self):
        constructed_word_result = ""

        for traversal_index in range(len(self.internal_character_buffer)):
            constructed_word_result = (
                constructed_word_result +
                self.internal_character_buffer[traversal_index]
            )

        return constructed_word_result


# Step 4: Define a manager class to coordinate everything
class HelloWorldCoordinator:

    def __init__(self):
        self.repository_instance = None
        self.searcher_instance = None
        self.engine_instance = None
        self.target_sequence_definition = []

        self._setup_repository()
        self._setup_searcher()
        self._setup_engine()
        self._define_target_sequence()

    def _setup_repository(self):
        self.repository_instance = AlphabetRepository()

    def _setup_searcher(self):
        self.searcher_instance = AlphabetSearcher(
            self.repository_instance.get_storage_reference()
        )

    def _setup_engine(self):
        self.engine_instance = WordConstructionEngine(
            self.searcher_instance
        )

    def _define_target_sequence(self):

        self.target_sequence_definition = [
            'h','e','l','l','o',' ',
            'w','o','r','l','d'
        ]

    def execute_construction_sequence(self):

        for sequence_index in range(len(self.target_sequence_definition)):

            character_to_process = (
                self.target_sequence_definition[sequence_index]
            )

            self._process_single_character(character_to_process)

    def _process_single_character(self, character):

        validated_character = self._validate_character(character)

        if validated_character is True:

            self.engine_instance.append_character_to_internal_buffer(
                character
            )

    def _validate_character(self, character):

        for traversal_index in range(
            len(self.repository_instance.get_storage_reference())
        ):

            if (
                self.repository_instance.get_storage_reference()
                [traversal_index] == character
            ):
                return True

        return False

    def retrieve_final_output(self):
        return self.engine_instance.retrieve_constructed_word()


# Step 5: Define utility class for printing
class OutputDisplaySystem:

    def __init__(self, message):
        self.message = message

    def perform_output_operation(self):

        final_output_buffer = ""

        for traversal_index in range(len(self.message)):

            character = self.message[traversal_index]

            final_output_buffer = final_output_buffer + character

        self._execute_print(final_output_buffer)

    def _execute_print(self, buffer):
        print(buffer)


# Step 6: Define main execution controller
class MainExecutionController:

    def __init__(self):
        self.coordinator_instance = None
        self.output_system_instance = None

    def run(self):

        self._initialize_coordinator()

        self._run_construction()

        result = self._fetch_result()

        self._initialize_output_system(result)

        self._display_output()

    def _initialize_coordinator(self):
        self.coordinator_instance = HelloWorldCoordinator()

    def _run_construction(self):
        self.coordinator_instance.execute_construction_sequence()

    def _fetch_result(self):
        return self.coordinator_instance.retrieve_final_output()

    def _initialize_output_system(self, result):
        self.output_system_instance = OutputDisplaySystem(result)

    def _display_output(self):
        self.output_system_instance.perform_output_operation()


# Step 7: Entry point function
def program_entry_point():

    execution_controller = MainExecutionController()

    execution_controller.run()


# Step 8: Execute program
if __name__ == "__main__":

    program_entry_point()

# ============================================
# END OF EXTREMELY OVERENGINEERED PROGRAM
# ============================================