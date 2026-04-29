#include <cctype>
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <vector>
using namespace std;

const string PROFESSOR_FILE = "professors.json";
const string TIMETABLE_FILE = "timetable.json";

struct Node {
    map<char, Node*> mp;
    bool isEnd = false;
};

class PrefixTree {
    Node* root;

    string clean(string s) {
        while (!s.empty() && isspace((unsigned char)s.front())) s.erase(s.begin());
        while (!s.empty() && isspace((unsigned char)s.back())) s.pop_back();
        for (char& ch : s) ch = tolower((unsigned char)ch);
        return s;
    }

    void collect(Node* curr, string word, vector<string>& ans) {
        if (curr->isEnd) ans.push_back(word);
        for (auto x : curr->mp) collect(x.second, word + x.first, ans);
    }

public:
    PrefixTree() { root = new Node(); }

    void insert(string word) {
        Node* curr = root;
        word = clean(word);
        for (char ch : word) {
            if (curr->mp.find(ch) == curr->mp.end()) curr->mp[ch] = new Node();
            curr = curr->mp[ch];
        }
        curr->isEnd = true;
    }

    bool search(string word) {
        Node* curr = root;
        word = clean(word);
        for (char ch : word) {
            if (curr->mp.find(ch) == curr->mp.end()) return false;
            curr = curr->mp[ch];
        }
        return curr->isEnd;
    }

    vector<string> startsWith(string prefix) {
        Node* curr = root;
        prefix = clean(prefix);
        vector<string> ans;
        for (char ch : prefix) {
            if (curr->mp.find(ch) == curr->mp.end()) return ans;
            curr = curr->mp[ch];
        }
        collect(curr, prefix, ans);
        return ans;
    }
};

string esc(string s) {
    string ans;
    for (char ch : s) {
        if (ch == '\\' || ch == '"') ans += '\\';
        ans += ch;
    }
    return ans;
}

vector<string> loadNames() {
    ifstream file(PROFESSOR_FILE);
    vector<string> names;
    if (!file) return names;

    string text((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    bool inside = false;
    string word;
    for (char ch : text) {
        if (ch == '"') {
            if (inside) names.push_back(word);
            inside = !inside;
            word.clear();
        } else if (inside) word += ch;
    }
    return names;
}

void saveNames(vector<string> names) {
    ofstream file(PROFESSOR_FILE);
    file << "[\n";
    for (int i = 0; i < (int)names.size(); i++)
        file << "  \"" << esc(names[i]) << "\"" << (i + 1 < (int)names.size() ? "," : "") << "\n";
    file << "]\n";
}

PrefixTree buildTrie(vector<string> names) {
    PrefixTree trie;
    for (string name : names) trie.insert(name);
    return trie;
}

struct Subject { string name, teacher; int credits; };
struct Cell { string subject, teacher; };

vector<string> days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"};
vector<string> slots = {"8-9 AM", "9-10 AM", "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM"};
vector<Subject> subjects = {
    {"DAA", "Teacher1", 4}, {"Java", "Teacher2", 4}, {"Automata", "Teacher3", 3}, {"Microprocessors", "Teacher4", 2},
    {"Lab1", "Teacher5", 2}, {"Lab2", "Teacher6", 2}, {"Lab3", "Teacher7", 2}, {"Lab4", "Teacher8", 2}
};

map<string, vector<Cell>> makeTimetable(int sections) {
    map<string, vector<Cell>> tables;
    set<string> teacherBusy;
    int total = days.size() * slots.size();

    for (int sec = 0; sec < sections; sec++) {
        string sectionName = "Section" + string(1, char('A' + sec));
        vector<Cell> cells(total, {"Free", ""});
        priority_queue<pair<int, int>> pq;
        for (int i = 0; i < (int)subjects.size(); i++) pq.push({subjects[i].credits, i});

        while (!pq.empty()) {
            int left = pq.top().first, index = pq.top().second;
            pq.pop();
            bool placed = false;

            for (int cell = 0; cell < total; cell++) {
                int d = cell / slots.size(), s = cell % slots.size();
                string key = subjects[index].teacher + days[d] + slots[s];
                if (cells[cell].subject == "Free" && teacherBusy.count(key) == 0) {
                    cells[cell] = {subjects[index].name, subjects[index].teacher};
                    teacherBusy.insert(key);
                    left--;
                    placed = true;
                    break;
                }
            }
            if (placed && left > 0) pq.push({left, index});
        }
        tables[sectionName] = cells;
    }
    return tables;
}

string timetableJson(map<string, vector<Cell>> tables) {
    string json = "{\n  \"days\": [";
    for (int i = 0; i < (int)days.size(); i++) json += "\"" + days[i] + "\"" + (i + 1 < (int)days.size() ? ", " : "");
    json += "],\n  \"slots\": [";
    for (int i = 0; i < (int)slots.size(); i++) json += "\"" + slots[i] + "\"" + (i + 1 < (int)slots.size() ? ", " : "");
    json += "],\n  \"sections\": {\n";

    int sectionCount = 0;
    for (auto table : tables) {
        json += "    \"" + table.first + "\": [\n";
        for (int i = 0; i < (int)table.second.size(); i++) {
            Cell c = table.second[i];
            json += "      [\"" + esc(c.subject) + "\", \"" + esc(c.teacher) + "\"]";
            if (i + 1 < (int)table.second.size()) json += ",";
            json += "\n";
        }
        json += "    ]";
        if (++sectionCount < (int)tables.size()) json += ",";
        json += "\n";
    }
    return json + "  }\n}\n";
}

void printMessage(bool success, string message) {
    cout << "{ \"success\": " << (success ? "true" : "false") << ", \"message\": \"" << esc(message) << "\" }";
}

void handleTrie(int argc, char* argv[]) {
    string op = argc > 2 ? argv[2] : "";
    string name = argc > 3 ? argv[3] : "";
    vector<string> names = loadNames();
    PrefixTree trie = buildTrie(names);

    if (op == "all") {
        cout << "{ \"success\": true, \"professors\": [";
        for (int i = 0; i < (int)names.size(); i++) cout << "\"" << esc(names[i]) << "\"" << (i + 1 < (int)names.size() ? ", " : "");
        cout << "] }";
    } else if (op == "insert") {
        if (name == "") printMessage(false, "Please enter a professor name.");
        else {
            if (!trie.search(name)) {
                names.push_back(name);
                saveNames(names);
            }
            printMessage(true, name + " added successfully.");
        }
    } else if (op == "search") {
        bool found = trie.search(name);
        printMessage(found, found ? name + " found in Trie." : name + " not found.");
    } else if (op == "prefix") {
        vector<string> ans = trie.startsWith(name);
        cout << "{ \"success\": true, \"matches\": [";
        for (int i = 0; i < (int)ans.size(); i++) cout << "\"" << esc(ans[i]) << "\"" << (i + 1 < (int)ans.size() ? ", " : "");
        cout << "] }";
    } else printMessage(false, "Unknown Trie command.");
}

void handleSchedule(int argc, char* argv[]) {
    int sections = 1;
    if (argc > 2) {
        try {
            sections = stoi(argv[2]);
        } catch (...) {
            sections = 1;
        }
    }

    if (sections < 1) sections = 1;
    if (sections > 26) sections = 26;
    string json = timetableJson(makeTimetable(sections));
    ofstream(TIMETABLE_FILE) << json;
    cout << json;
}

int main(int argc, char* argv[]) {
    string command = argc > 1 ? argv[1] : "";
    if (command == "trie") handleTrie(argc, argv);
    else if (command == "schedule") handleSchedule(argc, argv);
    else printMessage(false, "Use: main trie ... or main schedule ...");
}
