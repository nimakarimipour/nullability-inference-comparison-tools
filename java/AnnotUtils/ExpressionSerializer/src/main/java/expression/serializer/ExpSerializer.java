/*
 * MIT License
 *
 * Copyright (c) 2024 Nima Karimipour
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

package expression.serializer;

import static com.google.errorprone.BugPattern.SeverityLevel.SUGGESTION;

import com.google.auto.service.AutoService;
import com.google.errorprone.BugPattern;
import com.google.errorprone.VisitorState;
import com.google.errorprone.bugpatterns.BugChecker;
import com.google.errorprone.matchers.Description;
import com.google.errorprone.util.ASTHelpers;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.Tree;
import com.sun.tools.javac.code.Symbol;
import expression.serializer.location.SymbolLocation;

@AutoService(BugChecker.class)
@BugPattern(
    name = "ExpSerializer",
    altNames = {"NullableAnnotationLocator"},
    summary = "Locates existing Nullable annotations.",
    tags = BugPattern.StandardTags.STYLE,
    severity = SUGGESTION)
@SuppressWarnings("BugPatternNaming")
public class ExpSerializer extends BugChecker
    implements BugChecker.MemberSelectTreeMatcher, BugChecker.IdentifierTreeMatcher {

  private static final Serializer serializer = new Serializer();
  // not good practice but works for now :)
  private static final String DELIMITER = "#$@$#";

  @Override
  public Description matchMemberSelect(MemberSelectTree tree, VisitorState state) {
    serialize(tree, state);
    return Description.NO_MATCH;
  }

  @Override
  public Description matchIdentifier(IdentifierTree tree, VisitorState state) {
    serialize(tree, state);
    return Description.NO_MATCH;
  }

  private void serialize(Tree tree, VisitorState state) {
    Symbol.MethodSymbol enclMethod;
    MethodTree enclosingMethod = ASTHelpers.findEnclosingNode(state.getPath(), MethodTree.class);
    enclMethod = enclosingMethod == null ? null : ASTHelpers.getSymbol(enclosingMethod);
    Symbol.ClassSymbol enclClass = enclMethod == null ? null : enclMethod.enclClass();
    if (enclClass == null) {
      return;
    }
    SymbolLocation location = SymbolLocation.createLocationFromSymbol(ASTHelpers.getSymbol(tree));
    if (location == null || location.getPath() == null) {
      return;
    }
    String expString = tree.toString();
    Symbol symbol = ASTHelpers.getSymbol(tree);
    if (symbol instanceof Symbol.VarSymbol && symbol.isStatic()) {
      expString =
          symbol.enclClass() == null
              ? Serializer.serializeSymbol(symbol)
              : Serializer.serializeSymbol(symbol.enclClass())
                  + "."
                  + Serializer.serializeSymbol(symbol);
    }
    String builder =
        Serializer.serializeSymbol(enclClass)
            + DELIMITER
            + Serializer.serializeSymbol(enclMethod)
            + DELIMITER
            + Serializer.escapeSpecialCharacters(expString)
            + DELIMITER
            + location.tabSeparatedToString();
    serializer.serializeExp(builder);
  }
}
